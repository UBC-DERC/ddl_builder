import ddl_builder as dlb
import pytest

@pytest.fixture
def trySchema():
    tryScheme = dlb.Schema(name = 'newScheme', comment = 'A schema for testing.')
    return tryScheme

@pytest.fixture
def tryDb():
    return dlb.D3Database(dbname='dranky',
                        comment = 'This database',
                        owner = 'appuser',
                        extensions = [])
