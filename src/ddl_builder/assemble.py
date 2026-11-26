from psycopg import sql

from ddl_builder import D3Database

from .sub_class import D3Database


def build_statements(db: D3Database) -> list[sql.Composable]:
    """_Generate the full set of SQL statements from the ddlml_

    Args:
        db (D3Database): _The D3 data object generated from ddlml. _

    Returns:
        list[sql.Composable]: _A list of SQL statements (in the order they were run)_
    """
    statements: list[sql.Composable] = []
