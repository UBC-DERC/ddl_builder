from psycopg import sql
from dataclasses import dataclass

class table():
    name:str
    type:str
    comment:str
    columns:list[column]
    constraints:list[constraint]
    indexes:list[index]
    def __init__(name, type, comment, constraints, indexes):