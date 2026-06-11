from psycopg import sql
from .sub_class import StrictModel

class Column(StrictModel):
    name:str
    type:str
    comment:str
    nullable:bool = True
    def column_clause(self, table:str = None, schema:str = None, alter:bool = False) -> sql.Composed:
        """_Generate the column creation clause._

        This function will work either as part of a CREATE TABLE call or an ALTER TABLE call,
        depending on whether or not the `alter` flag is set.

        Args:
            table (_type_, optional): _Which table is this column a part of?_. Defaults to None.
            schema (_type_, optional): _Which schema is the table is?_. Defaults to None.
            alter (bool, optional): _Should we generate an ALTER TABLE statement?_. Defaults to False.

        Returns:
            sql.Composed: _A valid SQL statement to be used either to alter an existing table, or to add to a CREATE TABLE statement._
        """        
        clause = sql.SQL("{name} {type}").format(
            name=sql.Identifier(self.name),
            type=sql.SQL(self.type),   # trusted fragment, not an identifier
        )
        if not self.nullable:
            clause = sql.SQL("{} NOT NULL").format(clause)
        return clause