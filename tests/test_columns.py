from ddl_builder import Column
import pytest

def test_column_clause_nullable_default():
    col = Column(name="id", type="integer", comment="")
    assert render(col.column_clause()) == '"id" integer'

def test_column_clause_not_null():
    col = Column(name="id", type="integer", comment="", nullable=False)
    assert render(col.column_clause()) == '"id" integer NOT NULL'