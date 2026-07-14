from .sub_class import *
from .load_yaml import *

def ddl_from_dict(model:DDL_Dict)->D3Database:
    input = model.model_dump()
    print(input)
    newDB = D3Database(**input)
    return newDB
