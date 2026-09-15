from ddl_builder import Column

def test_column_clause_nullable_default():
    # The default should render without the not null constraint.
    col = Column(name="id", type="integer", comment = "Test comment")
    assert col.column_clause().as_string() == '"id" integer'

def test_column_clause_not_null():
    # If we add the not null constraint we should see it show up.
    col = Column(name="id", type="integer", comment="The comment.", nullable=False)
    assert col.column_clause().as_string() == '"id" integer NOT NULL'

def test_column_alter_clause_not_null():
    col = Column(name="id", type="integer", comment="Test comment.", nullable=False)
    assert col.column_clause(alter=True, table="my_table", schema="my_schema").as_string() == 'ALTER TABLE "my_schema"."my_table" ADD COLUMN "id" integer NOT NULL'
