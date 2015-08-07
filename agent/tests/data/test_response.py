# coding=utf-8
import pytest
import allure
from hamcrest import *


from comnsense_agent.data import Response
from comnsense_agent.data.data import Data


@allure.feature("Data")
@pytest.mark.parametrize("code", [0, 1, 99, 600, "test", "", None])
def test_response_invalid_code(code):
    with pytest.raises(Data.ValidationError):
        Response(code)


@allure.feature("Data")
@pytest.mark.parametrize("data", [None, "some data", "", u"василий"])
@pytest.mark.parametrize("code", [200, 201, 202, 204, 404])
def test_response(code, data):
    response = Response(code, data)
    assert_that(response.code, equal_to(code))
    assert_that(response.data, equal_to(data))


@allure.feature("Data")
@pytest.mark.parametrize("data", [None, "some data", "", u"василий"])
@pytest.mark.parametrize("code", [200, 201, 202, 204, 404])
def test_response_serialize(code, data):
    expected = Response(code, data)
    serialized = expected.serialize()
    response = Response.deserialize(serialized)
    assert_that(response, equal_to(expected))


@allure.feature("Data")
@pytest.mark.parametrize("helper, code", [
    (Response.ok, 200), (Response.created, 201),
    (Response.accepted, 202), (Response.nocontent, 204),
    (Response.notfound, 404)])
def test_response_helpers(helper, code):
    expected = Response(code)
    response = helper()
    assert_that(response, equal_to(expected))


@allure.feature("Data")
@pytest.mark.parametrize("data", [None, "some data", "", u"василий"])
@pytest.mark.parametrize("code", [200, 201, 202, 204, 404])
def test_response_repr(code, data):
    response = Response(code, data)
    assert_that(len(repr(response)), greater_than(0))
    assert_that(len(str(response)), greater_than(0))
