import ddl_builder as dlb

def test_simple_schema(trySchema):
    assert type(trySchema) is dlb.Schema, "The new scheme thing is not the right class."
    assert trySchema.name == 'newScheme', "We didn't create the right name."

