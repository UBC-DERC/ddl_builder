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
    """    
    dbname: str
    port: int
    user: str
    password: str
    host: str
    conn: psycopg.Connection
    connstring:dict
    def __init__(self, connstring:dict = None):
        load_dotenv()
        self.dbname = environ.get('dbname')
        self.port = environ.get('port')
        self.user = environ.get('user')
        self.host = environ.get('host')
        self.password = environ.get('password')
        if not connstring:
            self.connstring = {'dbname': self.dbname,
                            'port': self.port,
                            'user': self.user,
                            'password': self.password,
                            'host': self.host}
        else:
            if not type(connstring) is dict:
                raise TypeError("Your connection string must be a dict.")
            self.connstring = connstring
        self.conn = None
    def check(self):
        """_Check that our connection to the database is valid._

        Returns:
            _type_: _description_
        """        
        try:
            conn = psycopg.connect(**self.connstring)
        except psycopg.ProgrammingError as e:
            raise psycopg.ProgrammingError(f"Your connection string is likely malformed. Check that {self.connstring} meets the requirements.\n{e}")
        if not conn.broken:
            return True
        return False
    def connect(self, dbname = None):
        if dbname:
            self.connstring['dbname'] = dbname
        if self.conn:
            if not self.conn.closed:
                self.conn.close()
        self.conn = psycopg.connect(**self.connstring, row_factory = dict_row)
    def close(self):
        if not self.conn.closed:
            self.conn.close()
