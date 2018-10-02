import pytest
from cement import fs

@pytest.fixture(scope="function")
def tmp(request):
    t = fs.Tmp()
    yield t
    t.remove()
