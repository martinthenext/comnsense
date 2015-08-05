import pytest
import allure

from comnsense_agent.data import Response


@pytest.yield_fixture(params=[202, 201, 204, 200, 404])
def response(request):
    data = None
    if request.param == 200:
        data = ""
    yield Response(request.param, data)
