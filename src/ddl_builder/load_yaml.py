from pathlib import Path

import yaml
from data_model.object_classes import DDL_Dict


def read_yaml(filepath:Path)->DDL_Dict:
    """_Read YAML file from path._

    Args:
        filepath (PosixPath): _A valid file path pointing to a YAML database definition file._

    Returns:
        object: _The YAML object rendered as a python Dict._
    """
    with open(filepath) as fp:
        try:
            yaml_object = yaml.safe_load(fp)
        except yaml.YAMLError as exc:
            print(exc)
    return DDL_Dict(**yaml_object)
