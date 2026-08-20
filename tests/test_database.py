
def test_database_object(tryDb):
    assert tryDb.name == 'dranky', "We didn't properly set the database name."

