from pydantic import BaseModel, ConfigDict, model_validator
from enum import Enum
from pydantic import AfterValidator, Field
from typing_extensions import Self, Annotated
from psycopg import sql
import re

class StrictModel(BaseModel):
    """_Modification of the Base Model, no type conversion._

    Args:
        BaseModel (_BaseModel_): _Part of the Pydantic setup._
    """    
    model_config = ConfigDict(strict=True)

class Reference(StrictModel):
    """_Table Reference_

    A class to manage references between (or within) tables in the database.

    Args:
        table (_str_): _A valid table within the schema._
        column (_str_): A valid column within the table._
    """    
    table:str
    column:str

def needs_name(self)-> str:
    """_Check that the name provided is valid._

    We are establishing an internal style where 

    Raises:
        ValueError: _Raises a ValueError if the provided name does not meet the requirements._

    Returns:
        str: _description_
    """    
    pattern = r'^[a-z_]+$'
    match = re.match(pattern, self) is not None
    if not match:
        raise ValueError("Object name must contain only lowercase letters or an underscore.")
    return self
    
class ConstraintEnum(str, Enum):
    check = 'CHECK'
    unique = 'UNIQUE'
    unique_nulls_not_distinct = 'UNIQUE NULLS NOT DISTINCT'
    primary_key = 'PRIMARY KEY'
    foreign_key = 'REFERENCES'

class Constraint(StrictModel):
    definition: str | None = None
    name: Annotated[str, AfterValidator(needs_name)]
    comment:str
    type:Annotated[ConstraintEnum, Field(strict=False)] = ConstraintEnum.check
    reference:list[Reference] = []
    @model_validator(mode='after')
    def right_reference(self)-> Self:
        if self.type == ConstraintEnum.foreign_key and self.reference == []:
            raise ValueError("A FOREIGN KEY requires a valid reference.")
        return self
    def constraint_clause(self) -> sql.Composed:
        clause = sql.SQL(self.definition)
        if self.comment:
            clause = clause + sql.SQL('\n') + sql.SQL('COMMENT CONSTRAINT {} is {}').format(sql.Identifier(self.name), sql.Literal(self.comment))
        return clause

class Column(StrictModel):
    name: Annotated[str, AfterValidator(needs_name)]
    type:str
    comment:str
    nullable:bool = True
    def column_clause(self, alter:bool = False, table:str | None = None, schema:str | None = None) -> sql.Composed:
        if alter:
            if table is None or schema is None:
                raise ValueError("Altering a column requires both table and schema names.")
            clause = sql.SQL('ALTER TABLE {}.{} ADD COLUMN {} {}').format(
                sql.Identifier(schema),
                sql.Identifier(table),
                sql.Identifier(self.name),
                sql.Identifier(self.type)
            )
        else:
            clause = sql.SQL('{0} {1}').format(
                sql.Identifier(self.name),
                sql.Identifier(self.type)
            )
        if not self.nullable:
            clause = sql.SQL('{} NOT NULL').format(clause)
        return clause

class Index(StrictModel):
    name: Annotated[str, AfterValidator(needs_name)]
    comment:str
    type:str
    definition:str
    reference:list[Reference] = []
    def index_clause(self) -> sql.Composed:
        clause = sql.SQL(self.definition)
        if self.comment: 
            clause = clause + sql.SQL('COMMENT ON INDEX {} IS {}')
        return clause

class Table(StrictModel):
    name: Annotated[str, AfterValidator(needs_name)]
    type: str = 'BASE TABLE'
    comment: str
    columns: list[Column] = []
    constraints: list[Constraint] = []
    indexes: list[Index] = []
    def table_clause(self, schema:str) -> sql.Composed:
        clause = sql.SQL('CREATE TABLE {}.{}').format(
            sql.Identifier(schema),
            sql.Identifier(self.name))
        for i in self.columns:
            clause = clause + sql.SQL("\n") + i.column_clause()
        return clause + sql.SQL(";")
    def table_comments(self, schema:str) -> sql.Composed:
        clause = sql.SQL('COMMENT ON TABLE {}.{} IS {}').format(
            sql.Identifier(schema), sql.Identifier(self.name), sql.Literal(self.comment))
        return clause + sql.SQL(";")

class Schema(StrictModel):
    name: Annotated[str, AfterValidator(needs_name)]
    tables: list[Table] = []
    comment: str
    def schema_clause(self) -> sql.Composed:
        clause = sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(self.name))
        return clause + sql.SQL(";")

class D3Database(StrictModel):
    schemas: list[Schema] = []
    dbname: Annotated[str, AfterValidator(needs_name)]
    comment: str | None = None
    owner: str = 'postgres'
    extensions: list[str] = []
    encoding: str = 'UTF8'
    locale: str = 'en_CA'
    def database_clause(self) -> sql.Composed:
        clause = sql.SQL("""
                         CREATE DATABASE {} OWNER = {} ENCODING={} LOCALE={} TEMPLATE=''template0'
                         """).format(
            sql.Identifier(self.dbname),
            sql.Literal(self.owner),
            sql.Literal(self.encoding),
            sql.Literal(self.locale)
        )
        return clause + sql.SQL(";")
    def extension_clauses(self) -> list[sql.Composed]:
        clauses = []
        for ext in self.extensions:
            clause = sql.SQL('CREATE EXTENSION IF NOT EXISTS {}').format(sql.Identifier(ext))
            clauses.append(clause + sql.SQL(";"))
        return clauses
