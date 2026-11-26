from ddlml.object_classes import ConstraintType
from psycopg import sql

from .sub_class import D3Database


def build_statements(db: D3Database) -> list[sql.Composable]:
    """_Generate the full set of SQL statements from the ddlml_

    Args:
        db (D3Database): _The D3 data object generated from ddlml. _

    Returns:
        list[sql.Composable]: _A list of SQL statements (in the order they were run)_
    """
    statements: list[sql.Composable] = []

    # The extensions live up at the `db` level, so lets add them first:
    statements += db.extension_clauses()

    # Then we have to add each schema:
    for schema in db.schemas:
        statements.append(schema.schema_clause())

    # Then we add the tables, and after we declare each table, we add the comments:
    for schema in db.schemas:
        for table in schema.tables:
            statements.append(table.table_clause(schema.name))
            statements.append(table.table_comments(schema.name))
            for constraint in table.constraints:
                # We can add all the constraints, but not foreign keys, because the
                # dependent table may not exist yet.
                if constraint.type != ConstraintType.foreign_key:
                    statements.append(constraint.constraint_comments(schema.name, table.name))

    # All of the indexes are added as `Alter Table` statements so we should be able to add them okay
    # I'm adding them before the foreign keys, but I'm not actually sure it matters.
    for schema in db.schemas:
        for table in schema.tables:
            for index in table.indexes:
                statements.append(index.index_clause())
                statements.append(index.index_comments(schema.name))

    # After all the tables are actually created, loop back and add the foreign keys:
    for schema in db.schemas:
        for table in schema.tables:
            for constraint in table.constraints:
                if constraint.type == ConstraintType.foreign_key:
                    statements.append(constraint.fk_alter_table_clause(schema.name, table.name))
                    statements.append(constraint.constraint_comments(schema.name, table.name))

    return statements


def render_script(db: D3Database) -> str:
    """The whole script as text, one statement per paragraph, each ending in `;`."""
    lines: list[str] = []
    for statement in build_statements(db):
        text = statement.as_string().strip()
        # Some clause methods end with a semicolon and some don't. Until they
        # agree, remove any that are there and add exactly one.
        lines.append(text.rstrip(";").rstrip() + ";")
    return "\n\n".join(lines) + "\n"
