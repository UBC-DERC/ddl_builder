
def main():
    from pathlib import Path

    from yaml import safe_dump, safe_load

    import ddl_builder as dlb

    with open(Path('settings.yaml'), 'r') as file:
        settings = safe_load(file)

    yamlPath = Path(settings.get('modelpath', '.')) / settings.get('modelfile', 'output.yaml')

    outcome = dlb.read_yaml(yamlPath)
    newDB = dlb.ddl_from_dict(outcome)

    outputPath = Path(settings.get('outputpath', '.')) / settings.get('outputfile', 'model_dump.yaml')
    outputPath.parent.mkdir(parents=True, exist_ok=True)
    with open(outputPath, 'w') as file:
        safe_dump(newDB.model_dump(), file, sort_keys=True)
    print(f'Wrote model dump to {outputPath}')

if __name__ == "__main__":
    main()
