import ddl_builder as dlb
import pytest
import psycopg

@pytest.fixture
def connection():
    return dlb.Cownection()

def test_Cownection_connect(connection):
    # We want to check that the database server is running
    assert connection.check()

def test_stable_connection(connection):
    connection.connect()
    if connection.conn:
        assert True
    else:
        assert False