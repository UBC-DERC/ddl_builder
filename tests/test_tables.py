from ddl_builder import Column, Table, Index
import pytest

@pytest.fixture
def single_column():
    return Column(name="id", type="integer", comment="")

@pytest.fixture
def double_column():
    return [Column(name="name", type="text", comment="", nullable=False),
            Column(name="age", type="integer", comment="")]

@pytest.fixture
def btree_index():
    return Index(name="idx_name", type="btree", comment="", definition="CREATE INDEX idx_name ON users (name);")


def test_new_table(single_column):
    table = Table(name="users", comment="A table for users.", columns=[single_column])
    assert table.name == "users"
    assert table.comment == "A table for users."
    assert len(table.columns) == 1
    assert table.columns[0].name == "id"
    assert table.columns[0].type == "integer"
    assert table.columns[0].comment == ""

def test_render_table_single(single_column):
    table = Table(name="users", comment="A table for users.", columns=[single_column])
    expected_clause = 'CREATE TABLE "public"."users"\n"id" "integer";'
    print(table.table_clause(schema="public").as_string())
    assert table.table_clause(schema="public").as_string() == expected_clause


def test_render_table_double_not_null(double_column):
    table = Table(name="users", comment="A table for users.", columns=double_column)
    expected_clause = 'CREATE TABLE "public"."users"\n"name" "text" NOT NULL\n"age" "integer";'
    print(table.table_clause(schema="public").as_string())
    assert table.table_clause(schema="public").as_string() == expected_clause

def test_index_clause(btree_index):
    expected_clause = 'CREATE INDEX idx_name ON users (name);'
    assert btree_index.index_clause().as_string() == expected_clause
