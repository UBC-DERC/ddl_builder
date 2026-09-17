import pytest

from ddl_builder import Column, Index, Table

@pytest.fixture
def single_column():
    return Column(name="id", type="integer", comment="This is a column")

@pytest.fixture
def double_column():
    return [Column(name="name", type="text", comment="Column one", nullable=False),
            Column(name="age", type="integer", comment="Column two")]

def test_render_table_single(single_column):
    table = Table(name="users", comment="A table for users.", columns=[single_column])
    expected_clause = 'CREATE TABLE "public"."users"(\n\t"id" integer\n\t);'
    print(table.table_clause(schema="public").as_string())
    assert table.table_clause(schema="public").as_string() == expected_clause


def test_render_table_double_not_null(double_column):
    table = Table(name="users", comment="A table for users.", columns=double_column)
    expected_clause = 'CREATE TABLE "public"."users"(\n\t"name" text NOT NULL,\n\t"age" integer\n\t);'
    print(table.table_clause(schema="public").as_string())
    assert table.table_clause(schema="public").as_string() == expected_clause

def test_render_table_no_columns_fails():
    with pytest.raises(ValueError):
        table = Table(name="users", comment="A table for users.", columns=[])
        table.table_clause(schema="public")