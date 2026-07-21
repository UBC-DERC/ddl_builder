from ddl_builder import Column

def test_column_clause_nullable_default():
    col = Column(name="id", type="integer", comment="")
    assert col.column_clause().as_string() == '"id" "integer"'

def test_column_clause_not_null():
    col = Column(name="id", type="integer", comment="", nullable=False)
    assert col.column_clause().as_string() == '"id" "integer" NOT NULL'

def test_column_alter_clause_not_null():
    col = Column(name="id", type="integer", comment="", nullable=False)
    assert col.column_clause(alter=True, table="my_table", schema="my_schema").as_string() == 'ALTER TABLE "my_schema"."my_table" ADD COLUMN "id" "integer" NOT NULL'