import ddl_builder as dlb
import pytest
import psycopg

@pytest.fixture
def connection():
    emptyConn = {
        'dbname': 'test',
        'port': 5432,
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost'}
    return dlb.Cownection(**emptyConn)

@pytest.fixture
def bad_connection():
    return dlb.Cownection(**{'aaa':12})

@pytest.fixture
def create_cows(connection, request):
    # Create a test database and remove it once the tests are done.
    db = dlb.D3Database(dbname='tester',
                        comment = 'This database',
                        owner = 'appuser',
                        extensions = ['pg_trgm'],
                        server = connection)
    #db.create()
    #assert db.check(), "The database wasn't created properly."
    # def delete_db():
    #    db.drop()
    #    assert db.check() is False, "The database wasn't deleted properly."
    #request.addfinalizer(delete_db)
    return db