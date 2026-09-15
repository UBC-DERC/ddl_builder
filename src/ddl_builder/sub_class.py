from typing import LiteralString, cast

from data_model.object_classes import (
    DDL_Dict,
    column_dict,
    constraint_dict,
    index_dict,
    reference_dict,
    schema_dict,
    table_dict,
)
from psycopg import sql
from psycopg.sql import Composed
from pydantic import model_validator

from .pg_type import pg_type


class Reference(reference_dict):
    """Reference - Inherits from data_model class `reference_dict`."""
    pass

class Constraint(constraint_dict):
    """Constraint - Inherits from data_model class `constraint_dict`."""
    @model_validator(mode="after")
    def validate_constraint_name(self) -> constraint_dict:
        if not self.name or self.name == "":
            raise ValueError("Constraint must have a name.")
        return self
    def constraint_clause(self) -> sql.Composed:
        clause = sql.SQL(obj=cast(typ=LiteralString, val=self.ddl))
        if self.comment:
            clause: Composed = (clause + sql.SQL('\n') +
                sql.SQL('COMMENT CONSTRAINT {} is {}')
                    .format(sql.Identifier(self.name), sql.Literal(self.comment)) +
                        sql.SQL(';'))
        else:
            clause: Composed = clause + sql.SQL(obj=';')
        return clause

class Column(column_dict):
    @model_validator(mode="after")
    def validate_column_comment(self) -> column_dict:
        if not self.comment or self.comment == "":
            raise ValueError("Column must have a comment.")
        return self
    """Column - Inherits from data_model class `column_dict`."""
    def column_clause(self, alter:bool = False,
                      table:str | None = None,
                      schema:str | None = None) -> sql.Composed:
        if alter:
            if table is None or schema is None:
                raise ValueError("Altering a column requires both table and schema names.")
            # Note that this is pushing out a LiteralString for the variable type,
            # However, the string is coming from our own validated yaml, or the user's yaml,
            # so it should be safe, or at least, user-responsible.
            # TODO: In the documentation for this class, and in other places, we should note that
            # this is a potential issue.
            clause = sql.SQL('ALTER TABLE {}.{} ADD COLUMN {} {}').format(
                sql.Identifier(schema),
                sql.Identifier(table),
                sql.Identifier(self.name),
                sql.SQL(cast(LiteralString, val=pg_type(self.type)))
            )
        else:
            clause = sql.SQL('{0} {1}').format(
                sql.Identifier(self.name),
                sql.SQL(cast(typ=LiteralString, val=pg_type(self.type)))
            )
        if not self.nullable:
            clause = sql.SQL('{} NOT NULL').format(clause)
        return clause

class Index(index_dict):
    """Index - Inherits from data_model class `index_dict`."""
    def index_clause(self) -> sql.Composed:
        clause = sql.SQL(obj=cast(typ=LiteralString, val=self.ddl)) + sql.SQL('')
        if self.comment:
            clause = clause + sql.SQL('COMMENT ON INDEX {} IS {}')
        return clause

class Table(table_dict):
    """Table - Inherits from data_model class `table_dict`."""
    columns: list[Column] = []
    constraints: list[Constraint] = []
    indexes: list[Index] = []
    def table_clause(self, schema:str) -> sql.Composed:
        clause = sql.SQL('CREATE TABLE {}.{}').format(
            sql.Identifier(schema),
            sql.Identifier(self.name))
        for i in self.columns:
            clause: Composed = clause + sql.SQL("\n") + i.column_clause()
        return clause + sql.SQL(obj=';')
    def table_comments(self, schema:str) -> sql.Composed:
        clause: Composed = sql.SQL('COMMENT ON TABLE {}.{} IS {}').format(
            sql.Identifier(schema), sql.Identifier(self.name), sql.Literal(self.comment))
        return clause

class Schema(schema_dict):
    """Schema - Inherits from data_model class `schema_dict`."""
    tables: list[Table] = []
    def schema_clause(self) -> sql.Composed:
        clause: Composed = sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(self.name))
        return clause + sql.SQL(";")

class D3Database(DDL_Dict):
    schemas: list[Schema] = []
    def database_clause(self) -> sql.Composed:
        clause: Composed = sql.SQL("""
                         CREATE DATABASE {} ENCODING={} LOCALE={} TEMPLATE='template0'
                         """).format(
            sql.Identifier(self.name),
            sql.Literal(self.encoding),
            sql.Literal(self.locale)
        )
        return clause + sql.SQL(";")
    def extension_clauses(self) -> list[sql.Composed]:
        clauses: list[Composed] = []
        for ext in self.extensions:
            clause: Composed = (sql.SQL('CREATE EXTENSION IF NOT EXISTS {}')
                .format(sql.Identifier(ext)))
            clauses.append(clause + sql.SQL(";"))
        return clauses
