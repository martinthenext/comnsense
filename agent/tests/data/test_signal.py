import allure
import pytest
import uuid
from hamcrest import *
import msgpack

from comnsense_agent.data import Signal
from comnsense_agent.data.data import Data


@allure.feature("Data")
@pytest.mark.parametrize(
    "code,data,raises",
    [(Signal.Code.Ready, None, None),
     (Signal.Code.Ready, 1, None),
     (Signal.Code.Ready, str(uuid.uuid1()), None),
     (Signal.Code.Stop, None, None),
     (Signal.Code.Stop, str(uuid.uuid1()), Data.ValidationError),
     (1, str(uuid.uuid1()), Data.ValidationError),
     (0, None, Data.ValidationError),
     (Signal.Code.Ready, uuid.uuid1(), Data.ValidationError)])
def test_signal_constructor(code, data, raises):
    if raises is not None:
        with pytest.raises(raises):
            Signal(code, data)
    else:
        Signal(code, data)


FIXTURES = [(Signal.Code.Stop, None),
            (Signal.Code.Ready, None),
            (Signal.Code.Ready, 1),
            (Signal.Code.Ready, str(uuid.uuid1()))]


@allure.feature("Data")
@pytest.mark.parametrize("code,data", FIXTURES)
def test_signal_property(code, data):
    signal = Signal(code, data)
    assert_that(signal.code, equal_to(code))
    assert_that(signal.data, equal_to(data))
    with pytest.raises(AttributeError):
        signal.code = code
    with pytest.raises(AttributeError):
        signal.data = data


@allure.feature("Data")
@pytest.mark.parametrize("code,data", FIXTURES)
def test_signal_deserialization(code, data):
    serialized = msgpack.packb([code.value, data], use_bin_type=True)
    allure.attach("signal", serialized)
    signal = Signal.deserialize(serialized)
    assert_that(signal.code, equal_to(code))
    assert_that(signal.data, equal_to(data))


@allure.feature("Data")
@pytest.mark.parametrize("code,data", FIXTURES)
def test_signal_deserialization(code, data):
    serialized = msgpack.packb([code.value, data], use_bin_type=True)
    allure.attach("signal", serialized)
    signal = Signal.deserialize(serialized)
    assert_that(signal.code, equal_to(code))
    assert_that(signal.data, equal_to(data))


@allure.feature("Data")
@pytest.mark.parametrize("code,data", FIXTURES)
def test_signal_serialization(code, data):
    expected = msgpack.packb([code.value, data], use_bin_type=True)
    allure.attach("expected", expected)
    serialized = Signal(code, data).serialize()
    allure.attach("serialized", serialized)
    assert_that(expected, equal_to(serialized))


@allure.feature("Data")
@pytest.mark.parametrize("code,data", FIXTURES)
def test_signal_repr(code, data):
    signal = Signal(code, data)
    representation = repr(signal)
    allure.attach("repr", representation)
    assert_that(len(representation), greater_than(0))


FIXTURES = [(Signal.Code.Stop, None),
            (Signal.Code.Ready, None),
            (Signal.Code.Ready, 1),
            (Signal.Code.Ready, str(uuid.uuid1()))]


@allure.feature("Data")
@pytest.mark.parametrize("code,data", FIXTURES[1:])
def test_signal_helper_ready(code, data):
    signal = Signal.ready(data)
    assert_that(signal.code, equal_to(code))
    assert_that(signal.data, equal_to(data))


@allure.feature("Data")
@pytest.mark.parametrize("code,data", FIXTURES[:1])
def test_signal_helper_ready(code, data):
    signal = Signal.stop()
    assert_that(signal.code, equal_to(code))
