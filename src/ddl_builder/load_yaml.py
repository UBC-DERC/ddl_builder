from pathlib import Path

import yaml
from pydantic import BaseModel


class column_dict(BaseModel):
    name:str
    type:str
    comment:str
    nullable:bool = True

class reference_dict(BaseModel):
    table:str
    columns:list[str]

class constraint_dict(BaseModel):
    name:str
    type:str | None = None
    comment:str | None = None
    ddl:str | None = None
    reference: list[reference_dict] = []

class index_dict(BaseModel):
    name:str
    type:str | None = None
    comment:str
    ddl:str
    reference:list[reference_dict] = []

class table_dict(BaseModel):
    name:str
    type:str = 'BASE TABLE'
    comment:str
    columns:list[column_dict]
    constraints:list[constraint_dict] = []
    indexes:list[index_dict] = []

class schema_dict(BaseModel):
    name:str
    comment:str | None = None
    tables:list[table_dict] | None = None

class DDL_Dict(BaseModel):
    encoding:str = 'UTF8'
    locale:str = 'en_CA'
    name:str
    comment:str | None = None
    extensions:list[str] = []
    schemas:list[schema_dict]

def read_yaml(filepath:Path)->DDL_Dict:
    """_Read YAML file from path._

    Args:
        filepath (PosixPath): _A valid file path pointing to a YAML database definition file._

    Returns:
        object: _The YAML object rendered as a python Dict._
    """    
    with open(filepath, 'r') as fp:
        try:
            yaml_object = yaml.safe_load(fp)
        except yaml.YAMLError as exc:
            print(exc)
    return DDL_Dict(**yaml_object)
