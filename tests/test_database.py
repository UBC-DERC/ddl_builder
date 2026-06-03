import pytest
import ddl_builder as dlb

def test_database_object(connection):
    db = dlb.d3database(dbname='dranky',
                        comment = 'This database',
                        owner = 'appuser',
                        extensions = [],
                        server = connection)
    assert db.dbname == 'dranky', "We didn't properly set the database name."
    assert db.server.dbname != 'dranky', "The server name only gets changed when the database is actually created."

def test_database_false(create_cows):
    assert create_cows.check() == True
    assert create_cows.dbname == 'tester', "The database was created, but it's name is wonky."

def test_extension_adding(create_cows):
    assert create_cows.check() == True
    create_cows.add_extensions('pg_trgm')
    query = """SELECT extname FROM pg_extension;"""
    with create_cows.server.conn.cursor() as cur:
        cur.execute(query)
        extensions = cur.fetchall()
    exte = [i['extname'] for i in extensions]
    assert all([i in exte for i in create_cows.extensions]), "Some of the extensions are not being created properly."
