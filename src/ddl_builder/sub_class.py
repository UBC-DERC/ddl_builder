from typing import LiteralString, cast

from ddlml.object_classes import (
    DDL_Dict,
    column_dict,
    constraint_dict,
    index_dict,
    reference_dict,
    schema_dict,
    table_dict,
    ConstraintType,
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

    @model_validator(mode="after")
    def validate_constraint_dll(self) -> constraint_dict:
        if (self.type.check or self.type.exclude) and not (self.ddl or self.ddl == ""):
            raise ValueError("CHECK and EXCLUDE constraints must have a DDL statement.")
        return self

    def constraint_clause(self) -> sql.Composed:
        match self.type:
            case ConstraintType.primary_key:
                return sql.SQL("CONSTRAINT {} PRIMARY KEY ({})").format(
                    sql.Identifier(self.name),
                    sql.SQL(", ").join(sql.Identifier(i) for i in self.columns),
                )
            case ConstraintType.unique:
                return sql.SQL("CONSTRAINT {} UNIQUE ({})").format(
                    sql.Identifier(self.name),
                    sql.SQL(", ").join(sql.Identifier(i) for i in self.columns),
                )
            case ConstraintType.unique_nulls_not_distinct:
                return sql.SQL("CONSTRAINT {} UNIQUE NULLS NOT DISTINCT ({})").format(
                    sql.Identifier(self.name),
                    sql.SQL(", ").join(sql.Identifier(i) for i in self.columns),
                )
            case ConstraintType.foreign_key:
                raise ValueError(
                    "Cannot create an inline constraint clause on a FOREIGN KEY with this package."
                )
            case ConstraintType.check | ConstraintType.exclude:
                if not self.ddl:
                    raise ValueError(
                        f"Constraint {self.name!r} of type {self.type} requires a "
                        "raw 'ddl' field — this type cannot be generated from structured fields."
                    )
                ddl_text = self.ddl.strip().rstrip(";")
                return sql.SQL(ddl_text)
            case _:
                raise ValueError(f"Unhandled constraint type: {self.type!r}")

    def constraint_comments(self, schema: str, table: str) -> sql.Composed:
        clause: Composed = sql.SQL("COMMENT ON CONSTRAINT {} ON {}.{} IS {}").format(
            sql.Identifier(self.name),
            sql.Identifier(schema),
            sql.Identifier(table),
            sql.Literal(self.comment),
        )
        return clause + sql.SQL(";")

    def fk_alter_table_clause(self, schema: str, table: str) -> sql.Composed:
        if not self.type.foregn_key:
            raise ValueError(f"fk_alter cannot be run on a {self.type} constraint.")
        if not self.reference:
            raise ValueError(f"The {self.name!r} FOREIGN KEY constraint requires a table/column reference.")

        local_cols = sql.SQL(", ").join(sql.Identifier(i) for i in self.columns)
        ref_cols = sql.SQL(", ").join(sql.Identifier(i) for i in self.reference.columns)

        return sql.SQL(
            "ALTER TABLE {schema}.{table} ADD CONSTRAINT {name} "
            "FOREIGN KEY ({local_cols}) REFERENCES {ref_schema}.{ref_table} ({ref_cols})"
        ).format(
            schema = sql.Identifier(schema),
            table = sql.Identifier(table),
            name = sql.Identifier(self.name),
            local_cols = local_cols,
            ref_schema = sql.Identifier(self.reference.schema),
            ref_table = sql.Identifier(self.reference.table),
            ref_cols = ref_cols
        )



class Column(column_dict):
    @model_validator(mode="after")
    def validate_column_comment(self) -> column_dict:
        if not self.comment or self.comment == "":
            raise ValueError("Column must have a comment.")
        return self

    """Column - Inherits from data_model class `column_dict`."""

    def column_clause(
        self, alter: bool = False, table: str | None = None, schema: str | None = None
    ) -> sql.Composed:
        if alter:
            if table is None or schema is None:
                raise ValueError("Altering a column requires both table and schema names.")
            # Note that this is pushing out a LiteralString for the variable type,
            # However, the string is coming from our own validated yaml, or the user's yaml,
            # so it should be safe, or at least, user-responsible.
            # TODO: In the documentation for this class, and in other places, we should note that
            # this is a potential issue.
            clause = sql.SQL("ALTER TABLE {}.{} ADD COLUMN {} {}").format(
                sql.Identifier(schema),
                sql.Identifier(table),
                sql.Identifier(self.name),
                sql.SQL(cast(LiteralString, val=pg_type(self.type))),
            )
        else:
            clause = sql.SQL("{0} {1}").format(
                sql.Identifier(self.name), sql.SQL(cast(typ=LiteralString, val=pg_type(self.type)))
            )
        if not self.nullable:
            clause = sql.SQL("{} NOT NULL").format(clause)
        return clause


class Index(index_dict):
    """Index - Inherits from data_model class `index_dict`."""

    def index_clause(self) -> sql.Composed:
        clause = sql.SQL(obj=cast(typ=LiteralString, val=self.ddl)) + sql.SQL("\n")
        if self.comment and self.comment != "":
            clause = clause + sql.SQL("COMMENT ON INDEX {} IS {}").format(
                sql.Identifier(self.name), sql.Literal(self.comment)
            )
        return clause


class Table(table_dict):
    """Table - Inherits from data_model class `table_dict`."""

    columns: list[Column] = []
    constraints: list[Constraint] = []
    indexes: list[Index] = []

    def table_clause(self, schema: str) -> sql.Composed:
        if len(self.columns) == 0:
            raise ValueError("Table must have at least one column.")
        clause = sql.SQL("CREATE TABLE {}.{}(\n\t").format(
            sql.Identifier(schema), sql.Identifier(self.name)
        )
        for i in self.columns[:-1]:
            clause: Composed = clause + i.column_clause() + sql.SQL(",\n\t")
        # No terminating comma here, so we can manage constraints as well.
        clause: Composed = clause + self.columns[-1].column_clause()
        # Now we add constraints, if any.
        # Note that we are not adding a comma before the first constraint,
        # because the last column already has a comma.
        if self.constraints and len(self.constraints) > 0:
            for i in self.constraints:
                clause: Composed = clause + sql.SQL(",\n\t") + i.constraint_clause()
        return clause + sql.SQL(obj="\n\t);")

    def table_comments(self, schema: str) -> sql.Composed:
        clause: Composed = sql.SQL("COMMENT ON TABLE {}.{} IS {}").format(
            sql.Identifier(schema), sql.Identifier(self.name), sql.Literal(self.comment)
        )
        return clause


class Schema(schema_dict):
    """Schema - Inherits from data_model class `schema_dict`."""

    tables: list[Table] = []

    def schema_clause(self) -> sql.Composed:
        clause: Composed = sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.name))
        return clause + sql.SQL(";")


class D3Database(DDL_Dict):
    schemas: list[Schema] = []

    def database_clause(self) -> sql.Composed:
        clause: Composed = sql.SQL("""
                         CREATE DATABASE {} ENCODING={} LOCALE={} TEMPLATE='template0'
                         """).format(
            sql.Identifier(self.name), sql.Literal(self.encoding), sql.Literal(self.locale)
        )
        return clause + sql.SQL(";")

    def extension_clauses(self) -> list[sql.Composed]:
        clauses: list[Composed] = []
        for ext in self.extensions:
            clause: Composed = sql.SQL("CREATE EXTENSION IF NOT EXISTS {}").format(
                sql.Identifier(ext)
            )
            clauses.append(clause + sql.SQL(";"))
        return clauses
