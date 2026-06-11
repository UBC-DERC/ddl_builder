
def test_database_object(tryDb):
    assert tryDb.dbname == 'dranky', "We didn't properly set the database name."

