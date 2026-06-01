import pytest
import ddl_builder as dlb


def test_simple_schema():
    tryScheme = dlb.schema(name = 'newScheme')
    assert type(tryScheme) is dlb.schema, "The new scheme thing is not the right class."
    assert tryScheme.name == 'newScheme', "We didn't create the right name."

def test_add_scheme(create_cows):
    tryScheme = dlb.schema(name = 'newScheme')
    create_cows.add_schema(dbSchema = tryScheme, create = True)
    assert create_cows.schema[0].name == 'newScheme', "The scheme wasn't added to the database."