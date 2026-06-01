from psycopg import sql
from dataclasses import dataclass

class schema():
    name: str
    tables: list
    def __init__(self, name):
        self.name = name
        self.tables = []
    
    