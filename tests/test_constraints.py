import pytest

from ddl_builder import Constraint, Reference

def test_check_constraint_no_ddl_fails():
    with pytest.raises(ValueError):
        Constraint(name="check",
                   type="CHECK",
                   comment="Peanut",
                   columns=["bonus"])


def test_exclude_constraint_no_ddl_fails():
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


def test_unique_nn_constraint_two_columns_no_ddl():
    cstr = Constraint(name="pk_key",
                      type="UNIQUE NULLS NOT DISTINCT",
                      comment="Hey there.",
                      ddl = "",
                      columns=["first", "second"],
                      references = None)
    assert cstr.constraint_clause().as_string() == 'CONSTRAINT "pk_key" UNIQUE NULLS NOT DISTINCT ("first", "second")'

def test_check_constraint_with_ddl_passes():
    cstr = Constraint(name="check",
                      type="CHECK",
                      comment="Peanut",
                      columns=["bonus"],
                      ddl="CHECK (bonus > 100)")
    assert cstr.constraint_clause().as_string() == cstr.ddl


def test_exclude_constraint_with_ddl_passes():
    cstr = Constraint(name="exclude",
                      type="EXCLUDE",
                      comment="Peanut",
                      columns=["bonus"],
                      ddl="CONSTRAINT exclude EXCLUDE (bonus < 100)")
    assert cstr.constraint_clause().as_string() == cstr.ddl
    
def test_foreign_key_constraint_clause_fails():
    cstr = Constraint(name="exclude",
                      type="FOREIGN KEY",
                      comment="Peanut",
                      columns=["bonus"],
                      references=Reference(table="banana", columns=["one"]),
                      ddl="CONSTRAINT exclude EXCLUDE (bonus < 100)")
    with pytest.raises(ValueError):
        cstr.constraint_clause()

def test_foreign_key_constraint_clause_fails():
    cstr = Constraint(name="exclude",
                      type="FOREIGN KEY",
                      comment="Peanut",
                      columns=["bonus"],
                      references=Reference(table="banana", columns=["one"]),
                      ddl="CONSTRAINT exclude EXCLUDE (bonus < 100)")
    
    fk_clause = cstr.fk_alter_table_clause(schema = "horse",
                                           table = cstr.references.table)

