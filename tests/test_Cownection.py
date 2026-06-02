import pytest
import psycopg
import ddl_builder as dlb

def test_Cownection_connect(connection):
    # We want to check that the database server is running
    assert connection.check(), "The database is not accepting connections."

def test_stable_connection(connection):
    connection.connect()
    if connection.conn:
        assert True, "The database is connecting and we're getting a psycopg connection object."
    else:
        assert False, "The database is connecting but the Cownection object is not returning the connection."

def test_switching_database(connection):
    connection.connect()
    connection.connect(dbname = 'postgres')
    assert connection.conn.info.dbname == 'postgres', "The database is not properly switching when a new dbname is given."
    assert connection.connstring().get('dbname') == 'appdb', "The connection string parameters are being changed."

def test_closing_database(connection):
    connection.connect()
    connection.close()
    assert connection.conn.info.status != 0, "The database connection was not closed properly using .close()."
