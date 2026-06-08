from pydantic import BaseModel, ValidationError
import pytest
from ddl_builder import D3Database, Schema, Table, Column, Constraint, Index, StrictModel

def test_all_models_are_basemodels():
    for cls in (D3Database, Schema, Table, Column, Constraint, Index):
        assert issubclass(cls, BaseModel)

def test_minimal_table_parses_from_dict():
    # round-trips a known-good YAML fragment
    Table.model_validate({
        'name': 'newTable',
        'type': 'BASE TABLE',
        'comment': 'A table for testing'
    })

def test_typo_data_type_is_rejected():
    with pytest.raises(ValidationError):
        Column.model_validate({"name": "id", "type": "varhcar"})

def test_fk_without_reference_is_rejected():
    with pytest.raises(ValidationError):
        Constraint.model_validate({"type": "foreign_key", "reference": [], "name": "testConstraint"})

def test_strict_model_does_not_allow_arbitrary_types():
    # If you remove the connection from the model, this guards the decision
    assert "arbitrary_types_allowed" not in StrictModel.model_config or \
           StrictModel.model_config["arbitrary_types_allowed"] is False

def test_optional_fields_accept_none():
    Constraint.model_validate({"name": "c", "comment": "", "definition": None})

def test_port_must_be_int_under_strict():
    with pytest.raises(ValidationError):
        Cownection.model_validate({"port": "5432"})  # documents strict behaviour

def test_constraint_enum_rejects_unknown_type():
    with pytest.raises(ValidationError):
        Constraint.model_validate({"name": "c", "comment": "", "type": "FORIEGN KEY"})
