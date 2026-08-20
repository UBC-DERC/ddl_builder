import pytest

import ddl_builder as dlb


@pytest.fixture
def trySchema():
    tryScheme = dlb.Schema(name = 'new_scheme', comment = 'A schema for testing.')
    return tryScheme

@pytest.fixture
def tryDb():
    return dlb.D3Database(name='dranky',
                        comment = 'This database',
                        owner = 'appuser',
                        extensions = [])
