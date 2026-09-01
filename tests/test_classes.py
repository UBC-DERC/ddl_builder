import pytest
from pydantic import BaseModel, ValidationError

from ddl_builder import (
    Column,
    Constraint,
    ConstraintEnum,
    D3Database,
    Index,
    Schema,
    StrictModel,
    Table,
)


def test_all_models_are_basemodels():
    for cls in (D3Database, Schema, Table, Column, Constraint, Index):
        assert issubclass(cls, BaseModel)

def test_minimal_table_parses_from_dict():
    # round-trips a known-good YAML fragment
    Table.model_validate({
        'name': 'newtable',
        'type': 'BASE TABLE',
        'comment': 'A table for testing'
    })

def test_column_rejected_without_comment():
    with pytest.raises(ValidationError):
        Column.model_validate({"name": "id", "type": "varhcar"})

def test_fk_without_reference_is_rejected():
    with pytest.raises(ValidationError, match='FOREIGN KEY'):
        Constraint.model_validate({
            "type": "REFERENCES",
            "reference": [],
            "comment": "A test",
            "name": "test_constraint"})
        
def test_fk_with_reference_parses():
    # The counter example to the above.
    c = Constraint.model_validate({
        "name": "fk_test",
        "comment": "",
        "type": "REFERENCES",
        "reference": [{"table": "cows", "column": "mooid"}],
    })
    assert c.type is ConstraintEnum.foreign_key

def test_strict_model_does_not_allow_arbitrary_types():
    # If you remove the connection from the model, this guards the decision
    assert "arbitrary_types_allowed" not in StrictModel.model_config or \
           StrictModel.model_config["arbitrary_types_allowed"] is False

def test_optional_fields_accept_none():
    Constraint.model_validate({"name": "c", "comment": "", "ddl": None, "reference": []})

def test_constraint_enum_rejects_unknown_type():
    # Catches a typo in the 'type' name:
    with pytest.raises(ValidationError):
        Constraint.model_validate({"name": "c", "comment": "", "type": "FORIEGN KEY"})

def test_constraint_without_reference_parses():
    # guards the `reference: list = []` default
    Constraint.model_validate({"name": "c", "comment": "", "type": "CHECK"})

def test_constraint_type_parses_from_string():
    # mirrors how YAML actually delivers the value
    c = Constraint.model_validate({"name": "c", "comment": "", "type": "CHECK"})
    assert c.type is ConstraintEnum.check
