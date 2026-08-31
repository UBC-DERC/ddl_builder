import pytest

from ddl_builder import Constraint


def test_constraint_noname():
    with pytest.raises(ValueError):
        Constraint(name="", type="PRIMARY KEY", definition="PRIMARY KEY (id)", comment="")

def test_constraint_noname_two():
    with pytest.raises(ValueError):
        Constraint(name="Abc9", type="PRIMARY KEY", definition="PRIMARY KEY (id)", comment="")

def test_constraint_foreign_key_no_reference():
    with pytest.raises(ValueError):
        Constraint(name="fk_test", type="FOREIGN KEY", definition="FOREIGN KEY (id) REFERENCES other_table(id)", comment="")

def test_constraint_compose():
    constraint = Constraint(name="chk_test", type="CHECK", definition="CHECK (value > 0)", comment="Check that value is positive")
    expected_clause = 'CHECK (value > 0)\nCOMMENT CONSTRAINT "chk_test" is \'Check that value is positive\';'
    assert constraint.constraint_clause().as_string() == expected_clause
