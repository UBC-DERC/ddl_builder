from psycopg import sql
from dataclasses import dataclass, field

class table():
    name:str
    type:str
    comment:str
    columns:list[column]
    constraints:list[constraint]
    indexes:list[index]
    def __init__(self, name, type, comment, constraints, indexes):
        self.name = name
        self.type = type
        self.comment = comment
        self.constraints = constraints
        self.indexes = indexes
