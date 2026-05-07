import ddl_builder as dlb

# First we want to point to the appropriate directory
yaml_models = dlb.read_files('../data_model/data_model/')

# Then we build the full yaml model
[dlb.read_yaml(i) for i in yaml_models]

# Ideally we'd then output as mermaid or some sort of flow chart

# Build some osrt of documentation

# And create the database model