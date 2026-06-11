from pydantic import BaseModel, ConfigDict, model_validator
from enum import Enum
from typing import Annotated
from pydantic import Field
from typing_extensions import Self

class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True)

class Reference(StrictModel):
    table:str
    column:str

class ConstraintEnum(str, Enum):
    check = 'CHECK'
    unique = 'UNIQUE'
    unique_nulls_not_distinct = 'UNIQUE NULLS NOT DISTINCT'
    primary_key = 'PRIMARY KEY'
    foreign_key = 'REFERENCES'

class Constraint(StrictModel):
    definition: str | None = None
    name:str
    comment:str
    type:Annotated[ConstraintEnum, Field(strict=False)] = ConstraintEnum.check
    reference:list[Reference] = []
    @model_validator(mode='after')
    def right_reference(self)-> Self:
        if self.type == ConstraintEnum.foreign_key and self.reference == []:
            raise ValueError("A FOREIGN KEY requires a valid reference.")
        return self

class Column(StrictModel):
    name:str
    type:str
    comment:str
    nullable:bool = True

class Index(StrictModel):
    name: str   
    comment:str
    type:str
    definition:str
    reference:list[Reference] = []

class Table(StrictModel):
    name: str
    type: str
    comment: str
    columns: list[Column] = []
    constraints: list[Constraint] = []
    indexes: list[Index] = []

class Schema(StrictModel):
    name: str
    tables: list[Table] = []
    comment: str

class D3Database(StrictModel):
    schemas: list[Schema] = []
    dbname: str
    comment: str | None = None
    owner: str = 'postgres'
    extensions: list[str] = []
    encoding: str = 'UTF8'
    locale: str = 'en_CA'
