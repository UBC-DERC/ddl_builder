from .sub_class import D3Database
from .load_yaml import DDL_Dict

def ddl_from_dict(model:DDL_Dict)->D3Database:
    input = model.model_dump()
    print(input)
    newDB = D3Database(**input)
    return newDB
