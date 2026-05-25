from psycopg import sql
from dataclasses import dataclass
from .server_class import Cownection

@dataclass
class d3database():
    server: Cownection
    name: str
    comment: str
    owner: str
    extensions: list
    encoding: str
    locale: str
    def __init__(self, name, comment, owner, extensions, encoding = 'UTF8', locale = 'en_CA', server = None):
        self.name = name
        self.comment = comment
        self.owner = owner
        self.extensions = extensions
        self.encoding = encoding
        self.locale = locale
        self.server = server
    def check(self):
        if self.server:
            db = self.server.conn.connect()
            query = sql.SQL("SELECT datname FROM pg_catalog.pg_database WHERE datname=%s")
            with db.cursor() as cur:
                cur.execute(query, (self.name,))
                result = cur.fetchone()
            if len(result) > 0:
                return True
            else: return False
    def create(self):
        query = sql.SQL("CREATE DATABASE {name} WITH OWNER = %s LOCALE = %s ENCODING = %s").format(
            name = sql.Identifier(self.name))
        with self.server.conn.cursor() as cur:
                cur.execute(query, (self.owner, self.locale, self.encoding, ))
        self.check()