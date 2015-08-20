import pytest
import random


@pytest.yield_fixture(scope="session")
def host():
    yield "127.0.0.1"


@pytest.yield_fixture(scope="session")
def port():
    yield random.choice(range(50000, 51000))
