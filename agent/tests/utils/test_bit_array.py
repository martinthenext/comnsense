import allure
import pytest
from hamcrest import *

from comnsense_agent.utils.bit_array import BitArray


@allure.feature("Utils")
@pytest.mark.parametrize("length", [None, 0, 1, 10, 100, 1000, 10000])
def test_bitarray_init(length):
    if length is None:
        ar = BitArray()
        length = 0
    else:
        ar = BitArray(length)
    assert_that(len(ar), greater_than_or_equal_to(length))


@allure.feature("Utils")
@pytest.mark.parametrize("length", [0, 1, 10, 100, 1000, 10000])
def test_bitarray_advance(length):
    ar = BitArray()
    ar.advance(length)
    assert_that(ar, greater_than_or_equal_to(length))


@allure.feature("Utils")
@pytest.mark.parametrize("length", [0, 1, 10, 100, 1000, 10000])
@pytest.mark.parametrize("pos", [0, 1, 10, 100, 1000])
def test_bitarray_items(length, pos):
    ar = BitArray(length)
    assert_that(ar[pos], is_(False))
    ar[pos] = True
    assert_that(ar[pos], is_(True))
    ar[pos] = False
    assert_that(ar[pos], is_(False))


@allure.feature("Utils")
@pytest.mark.parametrize("length", [0, 1, 10, 100, 1000, 10000])
@pytest.mark.parametrize("pos", [0, 1, 10, 100, 1000])
def test_bitarray_state(length, pos):
    ar = BitArray(length)
    ar[pos] = True
    state = ar.__getstate__()
    ar1 = BitArray()
    ar1.__setstate__(state)
    assert_that(ar, equal_to(ar1))
