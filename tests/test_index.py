from ddl_builder import Index
import pytest

@pytest.fixture
def btree_index():
    return Index(name="idx_name", type="btree", comment="", ddl="CREATE INDEX idx_name ON users (name);")

@pytest.fixture
def btree_index_with_comment():
    return Index(name="idx_name", type="btree", comment="This is an index.", ddl="CREATE INDEX idx_name ON users (name);")


def test_index_clause(btree_index):
    expected_clause = 'CREATE INDEX idx_name ON users (name);'
    assert btree_index.index_clause().as_string() == expected_clause

def test_index_with_comment(btree_index_with_comment):
    expected_clause = 'CREATE INDEX idx_name ON users (name);COMMENT ON INDEX \"idx_name\" IS \'This is an index.\''
    assert btree_index_with_comment.index_clause().as_string() == expected_clause
