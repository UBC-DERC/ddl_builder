import yaml
def read_yaml(filepath:PosixPath)->Dict:
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
    return yaml_object
