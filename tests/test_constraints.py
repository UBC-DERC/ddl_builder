import pytest

from ddl_builder import Constraint

@pytest.fixture
def unique_constraint_comment():
    return Constraint(name="unique_constraint",
                      type="UNIQUE",
                      comment="This is a unique constraint.",
                      ddl="ALTER TABLE my_table ADD CONSTRAINT unique_constraint UNIQUE (column1);")

@pytest.fixture
def unique_constraint_no_comment():
    return Constraint(name="unique_constraint",
                      type="UNIQUE",
                      comment="",
                      ddl="ALTER TABLE my_table ADD CONSTRAINT unique_constraint UNIQUE (column1);")

@pytest.fixture
def unique_constraint_no_semi():
    return Constraint(name="unique_constraint",
                      type="UNIQUE",
                      comment="",
                      ddl="ALTER TABLE my_table ADD CONSTRAINT unique_constraint UNIQUE (column1)")


def test_unique_constraint_comment(unique_constraint_comment):
    expected_clause = 'ALTER TABLE my_table ADD CONSTRAINT unique_constraint UNIQUE (column1);\nCOMMENT CONSTRAINT "unique_constraint" is \'This is a unique constraint.\';'
    assert unique_constraint_comment.constraint_clause().as_string() == expected_clause

def test_unique_constraint_no_comment(unique_constraint_no_comment):
    expected_clause = 'ALTER TABLE my_table ADD CONSTRAINT unique_constraint UNIQUE (column1);'
    assert unique_constraint_no_comment.constraint_clause().as_string() == expected_clause

def test_unique_constraint_no_semi(unique_constraint_no_semi):
    expected_clause = 'ALTER TABLE my_table ADD CONSTRAINT unique_constraint UNIQUE (column1);'
    assert unique_constraint_no_semi.constraint_clause().as_string() == expected_clause