
def main():
    import ddl_builder as dlb
    from yaml import safe_load
    from pathlib import Path

    with open(Path('settings.yaml'), 'r') as file:
        settings = safe_load(file)

    yamlPath = Path(settings.get('modelpath', '.')) / settings.get('modelfile', 'output.yaml')

    outcome = dlb.read_yaml(yamlPath)
    print(outcome)
        
if __name__ == "__main__":
    main()
