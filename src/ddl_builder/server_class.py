from dataclasses import dataclass
import psycopg
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
    def __init__(self):
        load_dotenv()
        self.dbname = environ.get('dbname')
        self.port = environ.get('port')
        self.user = environ.get('user')
        self.host = environ.get('host')
        self.password = environ.get('password')
        self.connstring = {'dbname': self.dbname,
                        'port': self.port,
                        'user': self.user,
                        'password': self.password,
                        'host': self.host}
        self.conn = None
    def check(self):
        try:
            with psycopg.connect(**self.connstring) as conn:
                if conn.broken:
                    return False
                return True
        except:
            print("Connection Error")
    def connect(self):
        self.conn = psycopg.connect(**self.connstring)