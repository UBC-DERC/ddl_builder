import ddl_builder as dlb
import pytest
import psycopg

@pytest.fixture
def connection():
    return dlb.Cownection()

@pytest.fixture
def bad_connection():
    return dlb.Cownection(connstring = {'aaa':12})

@pytest.fixture
def create_cows(connection, request):
    # Create a test database and remove it once the tests are done.
    db = dlb.d3database(dbname='tester',
                        comment = 'This database',
                        owner = 'appuser',
                        extensions = ['pg_trgm'],
                        server = connection)
    db.create()
    def delete_db():
        db.drop()
    request.addfinalizer(delete_db)
    return db