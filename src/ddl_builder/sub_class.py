from pydantic import BaseModel, ConfigDict, Field, SecretStr
from typing import Any
import psycopg
from enum import Enum
from dataclasses import dataclass
from psycopg.rows import dict_row
from dotenv import load_dotenv
from os import environ

class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True)

class Reference(StrictModel):
    table:str
    column:str

class ConstraintEnum(str, Enum):
    check = 'CHECK'
    not_null = 'NOT NULL'
    unique = 'UNIQUE'
    unique_nulls_not_distinct = 'UNIQUE NULLS NOT DISTINCT'
    primary_key = 'PRIMARY KEY'
    foreign_key = 'REFERENCES'

class Constraint(StrictModel):
    definition: str | None = None
    name:str
    comment:str
    type:ConstraintEnum = ConstraintEnum.check
    reference:list[Reference]

class Column(StrictModel):
    name:str
    type:str
    comment:str

class Index(StrictModel):
    name: str
    comment:str
    type:str
    definition:str
    reference:list[Reference]

class Table(StrictModel):
    name: str
    type: str
    comment: str
    columns: list[Column] = []
    constraints: list[Constraint] = []
    indexes: list[Index] = []

class Schema(StrictModel):
    name: str
    tables: list[Table] = []
    comment: str

class Cownection():
    """_A Connection to the (putative) Dairy Database._
       The connection assumes that we have a database server running somewhere. The
       `Cownection` class is simply a class to help manage our connections and ensure
       that they are functioning as expected.
       Some things to keep in mind, we should always be able to access the base `postgres`
       database, but should also support switching between databases (if we start in postgres and
       then create the new database).
    """    
    dbname: str = Field(default = 'postgres')
    port: int = Field(default = 5432)
    user: str = Field(default = 'postgres')
    password: SecretStr = Field(default = 'postgres')
    host: str = Field(default = 'localhost')
    conn: psycopg.Connection | None = None

class D3Database(StrictModel):
    schemas: list[Schema] = []
    dbname: str
    comment: str | None = None
    owner: str = 'postgres'
    extensions: list[str]
    encoding: str = 'UTF8'
    locale: str = 'en_CA'


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
        self.dbname = environ.get('dbname')
        self.port = environ.get('port')
        self.user = environ.get('user')
        self.host = environ.get('host')
        self.password = environ.get('password')
        self.conn = None
    def connstring(self, dbname:str = None):
        return {'dbname': dbname or self.dbname,
                'port': self.port,
                'user': self.user,
                'password': self.password,
                'host': self.host}
    def check(self, dbname:str = None):
        """_Check that our connection to the database is valid._

        Returns:
            _type_: _description_
        """        
        try:
            conn = psycopg.connect(**self.connstring(dbname))
        except psycopg.ProgrammingError as e:
            raise psycopg.ProgrammingError(f"Your connection string is likely malformed. Check that {self.connstring()} meets the requirements.\n{e}")
        if not conn.broken:
            return True
        return False
    def connect(self, dbname:str = None):
        if self.conn:
            if not self.conn.closed:
                self.conn.close()
        self.conn = psycopg.connect(**self.connstring(dbname), row_factory = dict_row)
    def close(self):
        if not self.conn.closed:
            self.conn.close()
