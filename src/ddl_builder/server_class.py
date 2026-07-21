from pydantic.v1 import NoneStr
from psycopg.connection import Connection
from typing import Any
from dataclasses import dataclass
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from os import environ

@dataclass
class Cownection:
    """_A Connection to the (putative) Dairy Database._
       The connection assumes that we have a database server running somewhere. The
       `Cownection` class is simply a class to help manage our connections and ensure
       that they are functioning as expected.

       Some things to keep in mind, we should always be able to access the base `postgres`
       database, but should also support switching between databases (if we start in postgres and
       then create the new database).
    """    
    dbname: str
    port: int
    user: str
    password: str
    host: str
    conn: psycopg.Connection
    def __init__(self):
        load_dotenv()
        self.dbname: str | None = environ.get(key='POSTGRES_DB')
        self.port: str | None = environ.get(key='POSTGRES_PORT')
        self.user: str | None = environ.get(key='POSTGRES_USER')
        self.host: str | None = environ.get(key='POSTGRES_HOST')
        self.password: str | None = environ.get(key='POSTGRES_PASSWORD')
        self.conn: psycopg.Connection | None = None
    def connstring(self, dbname:str|NoneStr = None):
        return {'dbname': dbname or self.dbname,
                'port': self.port,
                'user': self.user,
                'password': self.password,
                'host': self.host}
    def check(self, dbname:str|NoneStr = None):
        """_Check that our connection to the database is valid._

        Returns:
            _type_: _description_
        """        
        try:
            conn: Connection[tuple[Any, ...]] = psycopg.connect(**self.connstring(dbname))
        except psycopg.ProgrammingError as e:
            raise psycopg.ProgrammingError(f"Your connection string is likely malformed. Check that {self.connstring()} meets the requirements.\n{e}")
        if not conn.broken:
            return True
        return False
    def connect(self, dbname:str|None = None):
        if not dbname:
            dbname = self.dbname
        if self.conn:
            if not self.conn.closed:
                self.conn.close()
        self.conn: Connection[tuple[Any, ...]] = psycopg.connect(**self.connstring(dbname), row_factory = dict_row)
    def close(self):
        if not self.conn.closed:
            self.conn.close()
