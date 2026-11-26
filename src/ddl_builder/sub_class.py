import re
from typing import LiteralString, cast

from ddlml.object_classes import (
    ConstraintType,
    DDL_Dict,
    OnChangeType,
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

# Making sure we have a fixed set of reference types for fks.
_REFERENTIAL_ACTIONS: dict[OnChangeType, LiteralString] = {
    OnChangeType.no_action: "NO ACTION",
    OnChangeType.restrict: "RESTRICT",
    OnChangeType.cascade: "CASCADE",
    OnChangeType.set_null: "SET NULL",
    OnChangeType.set_default: "SET DEFAULT",
}

_CONSTRAINT = re.compile(pattern=r'^\s*CONSTRAINT\s+("?)([^"\s]+)\1\s+', flags=re.IGNORECASE)


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
        if self.type in (ConstraintType.check, ConstraintType.exclude) and not self.ddl:
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
                # These cases are a bit more complicated because it's difficult to generate the
                # different DDL clauses (greater than, less than, regex, whatever) in a way that
                # can pre-validate them. Once we decide we're accepting DDL, then we also have to
                # make sure it's structured in a way we want it.
                if not self.ddl:
                    raise ValueError(
                        f"Constraint {self.name!r} of type {self.type} requires a "
                        "raw 'ddl' field — this type cannot be generated from structured fields."
                    )
                # So check, using regex, to see if it starts with a range of `CONSTRAINT` prefixes
                # There's an extra strip in there just in case the ddl ends with ` ;`.
                cleanddl: str = self.ddl.strip().rstrip(";").strip()

                if match := _CONSTRAINT.match(string=cleanddl):
                    # Check the use of self.name when we have `CONSTRAINT`:
                    if match.group(2).lower() != self.name.lower():
                        raise ValueError(
                            f"Constraint {self.name!r}: the 'ddl' names a different "
                            f"constraint ({match.group(2)!r})."
                        )
                    cleanddl = cleanddl[match.end() :]
                return sql.SQL(obj="CONSTRAINT {} {}").format(
                    sql.Identifier(self.name),
                    sql.SQL(obj=cast(typ=LiteralString, val=cleanddl)),
                )
            case _:
                # This does not really get called, because we have a strict definition
                # around which constraints we have, but it's here because if I add one and
                # accidentally don't do anything with it, we'll get the error.
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
        if self.type != ConstraintType.foreign_key:
            raise ValueError(f"fk_alter cannot be run on a {self.type} constraint.")
        if not self.references:
            raise ValueError(
                f"The {self.name!r} FOREIGN KEY constraint requires a table/column reference."
            )
        if self.references.table is None:
            raise ValueError(f"There is no table name provided for {self.name}, check the ddlml.")

        local_cols = sql.SQL(", ").join(sql.Identifier(i) for i in self.columns)
        ref_cols = sql.SQL(", ").join(sql.Identifier(i) for i in self.references.columns)

        ref_schema = self.references.schema_ or schema

        clause: Composed = sql.SQL(
            "ALTER TABLE {schema}.{table} ADD CONSTRAINT {name} "
            "FOREIGN KEY ({local_cols}) REFERENCES {ref_schema}.{ref_table} ({ref_cols})"
        ).format(
            schema=sql.Identifier(schema),
            table=sql.Identifier(table),
            name=sql.Identifier(self.name),
            local_cols=local_cols,
            ref_schema=sql.Identifier(ref_schema),
            ref_table=sql.Identifier(self.references.table),
            ref_cols=ref_cols,
        )

        # Change now gives us our ON DELETE and ON UPDATE elements.
        if self.references.on_delete is not None:
            clause += sql.SQL(" ON DELETE ") + sql.SQL(
                _REFERENTIAL_ACTIONS[self.references.on_delete]
            )
        if self.references.on_update is not None:
            clause += sql.SQL(" ON UPDATE ") + sql.SQL(
                _REFERENTIAL_ACTIONS[self.references.on_update]
            )
        return clause


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

    def index_clause(self) -> sql.SQL:
        if self.ddl is None:
            raise ValueError(f"The index {self.name} requires a DDL field.")
        ddl_clean: str = self.ddl.strip().rstrip(";").strip()
        clause = sql.SQL(obj=cast(typ=LiteralString, val=ddl_clean))
        return clause

    def index_comments(self, schema: str) -> sql.Composed:
        clause = sql.SQL("COMMENT ON INDEX {}.{} IS {}").format(
            sql.Identifier(schema), sql.Identifier(self.name), sql.Literal(self.comment)
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
                # We add the foreign keys later.
                if i.type == ConstraintType.foreign_key:
                    continue
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
