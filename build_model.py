
def main():
    import ddl_builder as dlb
    import data_model as dm
    from yaml import safe_load
    from pathlib import Path

    with open(Path('settings.yaml'), 'r') as file:
        settings = safe_load(file)

    yamlPath = Path(settings['modelpath']) / 'output.yaml'

    with open(yamlPath, 'r') as file:
        database = safe_load(file)

    # We want to check that the database server is running
    result = dlb.Cownection()

    if not result.check():
        return None

    newDB = dlb.d3database(dbname=database.get('name'),
                              owner = 'appuser',
                              comment = database.get('comment'),
                              extensions = database.get('extensions', []),
                              encoding = database.get('encoding'),
                              locale = database.get('locale'),
                              server = result)
    assert newDB.check() is False, "The database seems to exist already."
    newDB.create()
    for i in database.get('schema'):
        schema = dlb.schema(**i)
        newDB.add_schema(schema, create = True)
    
if __name__ == "__main__":
    main()