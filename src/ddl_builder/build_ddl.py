from .load_yaml import DDL_Dict
from .sub_class import D3Database


def ddl_from_dict(model:DDL_Dict)->D3Database:
    input = model.model_dump()
    newDB = D3Database(**input)
    return newDB
