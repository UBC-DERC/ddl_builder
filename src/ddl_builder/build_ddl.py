from .sub_class import *




def ddl_from_dict(model:dict):
    newDB = D3Database(dbname=model.get('name'),
                              owner = 'appuser',
                              comment = model.get('comment'),
                              extensions = model.get('extensions', []),
                              encoding = model.get('encoding'),
                              locale = model.get('locale'))
    for i in model.get('schema'):
        newDB.schemas.append(Schema(name=i.get('name'),
                                                 comment=i.get('comment'),
                                                 constraints=i.get('constraints', []),
                                                 indexes=i.get('indexes', [])))