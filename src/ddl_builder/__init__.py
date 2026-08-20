"""ddl_builder public API.

Re-exports the classes and functions that make up the supported surface of the
package so callers can use ``from ddl_builder import Schema`` instead of reaching
into submodules. Anything not listed in ``__all__`` is considered internal.
"""

from .build_ddl import ddl_from_dict
from .cli import main
from .load_yaml import DDL_Dict, read_yaml
from .read_files import read_files
from .server_class import Cownection
from .sub_class import (
    Column,
    Constraint,
    ConstraintEnum,
    D3Database,
    Index,
    Reference,
    Schema,
    StrictModel,
    Table,
)

__all__ = [
    "Column",
    "Constraint",
    "ConstraintEnum",
    "Cownection",
    "D3Database",
    "DDL_Dict",
    "Index",
    "Reference",
    "Schema",
    "StrictModel",
    "Table",
    "ddl_from_dict",
    "main",
    "read_files",
    "read_yaml",
]
