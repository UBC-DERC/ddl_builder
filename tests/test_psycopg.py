from psycopg import sql


def test_psycopg_renders_without_connection():
    # guards the version assumption our golden tests rely on
    s = sql.SQL("SELECT {}").format(sql.Identifier("x"))
    assert s.as_string() == 'SELECT "x"'
