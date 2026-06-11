from psycopg import sql, DatabaseError
from .server_class import Cownection
@dataclass
class d3database():
    server: Cownection
    schema: dict
    dbname: str
    comment: str
    owner: str
    extensions: list
    encoding: str
    locale: str
    def __init__(self, dbname, comment, owner, extensions, encoding = 'UTF8', locale = 'en_CA', server = None):
        self.dbname = dbname
        self.comment = comment
        self.owner = owner
        self.schema = []
        self.extensions = extensions
        self.encoding = encoding
        self.locale = locale
        self.server = server
    def check(self):
        """_Check that a database actually exists on the server with the current settings._

        Returns:
            _bool_: _Did the operation work?_
        """        
        if self.server:
            db = self.server.conn
            if not db:
                self.server.connect(dbname="postgres")
                db = self.server.conn
            query = sql.SQL("SELECT datname FROM pg_catalog.pg_database WHERE datname=%s")
            with db.cursor() as cur:
                cur.execute(query, (self.dbname,))
                result = cur.fetchone()
            if result:
                outcome = True
            else: 
                outcome = False
            db.commit()
            return outcome
    def create(self, switch:bool = True):
        self.server.connect(dbname = 'postgres')
        # Have to set template0 here to allow new encodings and locales. If we use the
        # default template1 (excluding the `TEMPLATE` parameter) we get an error.
        query = sql.SQL("""
                    CREATE DATABASE {} WITH
                        OWNER = {}
                        LOCALE = {}
                        ENCODING = {}
                        TEMPLATE = 'template0'
                        """).format(
            sql.Identifier(self.dbname), sql.Identifier(self.owner), sql.Identifier(self.locale), sql.Identifier(self.encoding))
        # CREATE DATABASE cannot operate within a transaction, so we turn autocommit on and off.
        try:
            if not self.check():
                self.server.conn.autocommit = True
                with self.server.conn.cursor() as cur:
                        cur.execute(query)
                self.server.conn.autocommit = False
                self.server.dbname = self.dbname
                print(f"Created database {self.dbname} on the current server:\n{self.server.conn}")
            else:
                print(f"Database {self.dbname} already exists on the current server:\n{self.server.conn}")
        except Exception as e:
            self.server.conn.rollback()
            self.server.conn.autocommit = False
            print(e)
        self.connect()
        self.check()
    def add_extensions(self, extension:str = None):
        if not extension:
            self.extensions.append(extension)
        if self.server.conn is None:
            self.connect()
        if self.check():
            extensions = """SELECT extname FROM pg_extension;"""
            with self.server.conn.cursor() as cur:
                _ = cur.execute(extensions)
                ext = cur.fetchall()
            new_ext = [i for i in self.extensions if i not in ext]
            for j in new_ext:
                query = sql.SQL("""
                                CREATE EXTENSION IF NOT EXISTS {}
                                """).format(
                                    sql.Identifier(j)
                                )
                with self.server.conn.cursor() as cur:
                    cur.execute(query)
            self.server.conn.commit()
    def add_schema(self, dbSchema:sch, create:bool = True):
        self.connect()
        exist = [i for i in self.schema if i.name == dbSchema.name]
        if len(exist) > 0:
            raise ValueError("A schema of this name already exists in the database object.")
        self.schema.append(dbSchema)
        if create:
            self.create_schema(dbSchema.name)
    def check_schema(self, schemaName:str):
        try:
            schemaIndex = [i.name for i in self.schema].index(schemaName)
            return schemaIndex
        except ValueError:
            raise ValueError(f"The schema {schemaName} is not present in the current database")
    def check_table(self, schemaName:str, tableName:str)->tuple:
        schemaIndex = self.check_schema(schemaName)
        try:
            tableIndex = [i.name for i in self.schema[schemaIndex].tables].index(tableName)
            return (schemaIndex, tableIndex)
        except ValueError:
            raise ValueError(f"The table {tableName} is not present in the {schemaName} schema for this database.")
    def add_table(self, schemaName:str, dbTable:tbl.table, create:bool = True):
        try:
            tableIndex = self.check_table(schemaName, dbTable.name)
        except ValueError:
            schemaIndex = self.check_schema(schemaName)
            self.schema[schemaIndex].tables.append(dbTable)
    def create_table(self, dbSchema:str, dbTable:str):
        return None
    def create_schema(self, schemaName:str):
        self.connect()
        exist = [i for i in self.schema if i.name == schemaName]
        if len(exist) == 0:
            raise ValueError("No schema with this name exists in the current database object.")
        if self.check():
            newSchema = sql.SQL("""CREATE SCHEMA IF NOT EXISTS {};""").format(sql.Identifier(schemaName))
            with self.server.conn.cursor() as cur:
                _ = cur.execute(newSchema)
            self.server.conn.commit()
        elif not self.check():
            raise DatabaseError(f"Cannot connect to {self.server.connstring}")
    def drop_schema(self, dbSchema:sch):
        self.connect()
        if self.check():
            dropSchema = sql.SQL("""DROP SCHEMA IF EXISTS {};""").format(sql.Indentifier(dbSchema.name))
            try:
                with self.server.conn.cursor() as cur:
                        _ = cur.execute(dropSchema)
                self.server.conn.commit()
            except DatabaseError:
                print("Database error.")
    def drop(self):
        # We need to switch out of wherever we are.
        if self.dbname == 'postgres':
            raise ValueError("You cannot drop a database when you are connected to the defauly 'postgres' database.")
        self.server.connect(dbname='postgres')
        query = sql.SQL("""
                    DROP DATABASE IF EXISTS {}
                        """).format(
            sql.Identifier(self.dbname))
        # CREATE DATABASE cannot operate within a transaction, so we turn autocommit on and off.
        try:
            if self.check():
                self.server.conn.autocommit = True
                with self.server.conn.cursor() as cur:
                        cur.execute(query)
                self.server.conn.autocommit = False
                print(f"Removed database {self.dbname} on the current server:\n{self.conn}")
            else:
                print(f"Database {self.name} did not exist on the current server:\n{self.conn}")
        except Exception as e:
            self.server.conn.rollback()
            self.server.conn.autocommit = False
            print(e)
        self.check()
    def connect(self, dbname:str = None):
        if not dbname:
            dbname = self.dbname
        self.server.connect(dbname)

        