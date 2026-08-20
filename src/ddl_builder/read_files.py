from pathlib import Path


def read_files(filepath:str|Path)->object:
    if isinstance(filepath, str):
        path = Path(filepath)
    else:
        path: Path = filepath
    assert path.exists(), f"The path provided ({filepath}) is not a valid path/file/directory."
    assert path.is_dir(), "The path provided to read_files must be a directory."
    file_list: list[Path] = [child for child in path.glob(pattern='**/*.yaml')]
    return file_list