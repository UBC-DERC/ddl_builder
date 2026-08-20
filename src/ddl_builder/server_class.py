from dataclasses import dataclass
from os import environ
from typing import Any

import psycopg
from dotenv import load_dotenv
from psycopg.connection import Connection
from psycopg.rows import DictRow, dict_row


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
    name: str
    user: str
    password: str
    host: str
    port: int | None = 5432
    conn: psycopg.Connection | None = None
    def __init__(self):
        load_dotenv()
        self.name: str | None = environ.get(key='POSTGRES_DB')
        self.port: str | None = environ.get(key='POSTGRES_PORT')
        self.user: str | None = environ.get(key='POSTGRES_USER')
        self.host: str | None = environ.get(key='POSTGRES_HOST')
        self.password: str | None = environ.get(key='POSTGRES_PASSWORD')
        self.conn: psycopg.Connection | None = None
    def connstring(self, name:str | None = None):
        return {'name': name or self.name,
                'port': self.port,
                'user': self.user,
                'password': self.password,
                'host': self.host}
    def check(self, name:str|None = None):
        """_Check that our connection to the database is valid._

        Returns:
            _type_: _description_
        """        
        try:
            conn: Connection[tuple[Any, ...]] = psycopg.connect(**self.connstring(name))
        except psycopg.ProgrammingError as e:
            raise psycopg.ProgrammingError(f"Your connection string is likely malformed. Check that {self.connstring()} meets the requirements.\n{e}")
        return bool(not conn.broken)


    def connect(self, name:str|None = None):
        if not name:
            name = self.name
        if self.conn and not self.conn.closed:
            self.conn.close()
        self.conn: Connection[DictRow] = Connection[DictRow].connect(**self.connstring(name), row_factory = dict_row)
    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
