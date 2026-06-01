import ddl_builder as dlb

# We want to check that the database server is running
result = dlb.Cownection()

if result.check():
    database = dlb.d3database(name='dairy',
                              comment = 'This database',
                              owner = 'appuser',
                              extensions = [],
                              server = result)
    database.check()
    database.create()