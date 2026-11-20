from .sub_class import D3Database


def ddl_from_dict(model: D3Database) -> D3Database:
    input = model.model_dump()
    newDB = D3Database(**input)
    return newDB
