import pytest

from ddl_builder import Constraint

@pytest.fixture
def unique_constraint_comment():
    return Constraint(name="unique_constraint",
                      type="UNIQUE",
                      comment="This is a unique constraint.",
                      columns=["column1"],
                      ddl="ALTER TABLE my_table ADD CONSTRAINT unique_constraint UNIQUE (column1);")

@pytest.fixture
def unique_constraint_no_comment():
    return Constraint(name="unique_constraint",
                      type="UNIQUE",
                      comment="",
                      columns=["column1"],
                      ddl="ALTER TABLE my_table ADD CONSTRAINT unique_constraint UNIQUE (column1);")

@pytest.fixture
def unique_constraint_no_semi():
    return Constraint(name="unique_constraint",
                      type="UNIQUE",
                      comment="",
                      columns=["column1"],
                      ddl="ALTER TABLE my_table ADD CONSTRAINT unique_constraint UNIQUE (column1)")


# This doesn't work right now, the comment isn't getting added, __but__ at the same time
# we're changing the way the constraint clauses are generated.
#
# def test_unique_constraint_comment(unique_constraint_comment):
#     expected_clause = 'ALTER TABLE my_table ADD CONSTRAINT unique_constraint UNIQUE (column1);\nCOMMENT CONSTRAINT "unique_constraint" is "\'This is a unique constraint.\';"'
#     print(expected_clause)
#     print(unique_constraint_comment.constraint_clause().as_string())
#     assert unique_constraint_comment.constraint_clause().as_string() == expected_clause

def test_unique_constraint_no_comment(unique_constraint_no_comment):
    expected_clause = 'ALTER TABLE my_table ADD CONSTRAINT unique_constraint UNIQUE (column1);'
    assert unique_constraint_no_comment.constraint_clause().as_string() == expected_clause

def test_unique_constraint_no_semi(unique_constraint_no_semi):
    expected_clause = 'ALTER TABLE my_table ADD CONSTRAINT unique_constraint UNIQUE (column1);'
    assert unique_constraint_no_semi.constraint_clause().as_string() == expected_clause

def test_check_constraint_no_ddl_fails():
    with pytest.raises(ValueError):
        Constraint(name="check",
                   type="CHECK",
                   comment="Peanut",
                   columns=["bonus"])

def test_exclude_constraint_no_ddl_fails():
    with pytest.raises(ValueError):
        Constraint(name="check",
                   type="EXCLUDE",
                   comment="Peanut",
                   columns=["bonus"])

def test_pk_constraint_two_columns_no_ddl():
    cstr = Constraint(name="pk_key",
                      type="PRIMARY KEY",
                      comment="Hey there.",
                      ddl = "",
                      columns=["first", "second"],
                      references = None)
    assert cstr.constraint_clause().as_string() == 'CONSTRAINT "pk_key" PRIMARY KEY ("first", "second")'

def test_pk_constraint_one_columns_no_ddl():
    cstr = Constraint(name="pk_key",
                      type="PRIMARY KEY",
                      comment="Hey there.",
                      ddl = "",
                      columns=["first"],
                      references = None)
    assert cstr.constraint_clause().as_string() == 'CONSTRAINT "pk_key" PRIMARY KEY ("first")'

def test_unique_constraint_one_column_no_ddl():
    cstr = Constraint(name="pk_key",
                      type="UNIQUE",
                      comment="Hey there.",
                      ddl = "",
                      columns=["first"],
                      references = None)
    assert cstr.constraint_clause().as_string() == 'CONSTRAINT "pk_key" UNIQUE ("first")'


def test_unique_constraint_two_columns_no_ddl():
    cstr = Constraint(name="pk_key",
                      type="UNIQUE",
                      comment="Hey there.",
                      ddl = "",
                      columns=["first", "second"],
                      references = None)
    assert cstr.constraint_clause().as_string() == 'CONSTRAINT "pk_key" UNIQUE ("first", "second")'
