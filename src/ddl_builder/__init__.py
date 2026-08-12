"""ddl_builder public API.

Re-exports the classes and functions that make up the supported surface of the
package so callers can use ``from ddl_builder import Schema`` instead of reaching
into submodules. Anything not listed in ``__all__`` is considered internal.
"""

from .read_files import read_files
from .load_yaml import read_yaml, DDL_Dict
from .sub_class import (
    Schema,
    Table,
    Column,
    Constraint,
    Index,
    Reference,
    D3Database,
    StrictModel,
    ConstraintEnum,
)
from .server_class import Cownection
from .build_ddl import ddl_from_dict
from .cli import main

__all__ = [
    "read_files",
    "read_yaml",
    "DDL_Dict",
    "Schema",
    "Table",
    "Column",
    "Constraint",
    "Index",
    "Reference",
    "D3Database",
    "StrictModel",
    "ConstraintEnum",
    "Cownection",
    "ddl_from_dict",
    "main",
]
