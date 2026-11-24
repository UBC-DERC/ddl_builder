from .sub_class import D3Database
from ddlml.object_classes import DDL_Dict


def ddl_from_dict(model: DDL_Dict) -> D3Database:
    input = model.model_dump()
    newDB = D3Database(**input)
    return newDB
