import pytest
import ddl_builder as dlb
from psycopg import sql

def test_simple_schema():
    tryScheme = dlb.schema(name = 'newScheme')
    assert type(tryScheme) is dlb.schema, "The new scheme thing is not the right class."
    assert tryScheme.name == 'newScheme', "We didn't create the right name."

def test_add_clean_scheme_no_create(create_cows):
    tryScheme = dlb.schema(name = 'newScheme')
    create_cows.add_schema(dbSchema = tryScheme, create = False)
    assert create_cows.schema[0].name == 'newScheme', "The scheme wasn't added to the database."
    with create_cows.server.conn.cursor() as cur:
        query = sql.SQL("""
                        SELECT schema_name FROM information_schema.schemata
                        WHERE catalog_name = 'tester'
                        AND schema_name = 'newScheme';""")
        cur.execute(query)
        result = cur.fetchall()
        assert len(result) == 0, "The schema was created by accident."

def test_add_schema_already_exists(create_cows):
    tryScheme = dlb.schema(name = 'newScheme')
    create_cows.add_schema(dbSchema = tryScheme)
    with pytest.raises(ValueError):
        create_cows.add_schema(dbSchema = tryScheme)

def test_add_create_schema(create_cows):
    tryScheme = dlb.schema(name = 'newScheme')
    create_cows.add_schema(dbSchema = tryScheme, create = True)
    with create_cows.server.conn.cursor() as cur:
        query = sql.SQL("""
                        SELECT schema_name FROM information_schema.schemata
                        WHERE catalog_name = 'tester'
                        AND schema_name = 'newScheme';""")
        cur.execute(query)
        result = cur.fetchall()
        print(result)
        assert len(result) == 1, "The schema was not created."