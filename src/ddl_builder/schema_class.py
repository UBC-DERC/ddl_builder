from psycopg import sql
from dataclasses import dataclass

class schema():
    name: str
    tables: list
    comment: str
    def __init__(self, name, comment = "", tables = []):
        self.name = name
        self.tables = tables
        self.comment = comment    
    