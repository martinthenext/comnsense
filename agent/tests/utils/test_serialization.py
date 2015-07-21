import allure
import pytest
import mock
import random
from hamcrest import *
import itertools
import copy
import types

from ..fixtures.classes import CLASSES, simple_class_fields
from ..fixtures.classes import complex_class_fields

from comnsense_agent.utils.serialization import get_content
from comnsense_agent.utils.serialization import restore_content
from comnsense_agent.utils.serialization import Serializable


@allure.feature("Serialization")
@pytest.mark.parametrize("klass", CLASSES[1:],
                         ids=[x.__name__ for x in CLASSES[1:]])
def test_get_content(klass, complex_class_fields):
    attrs, expected = complex_class_fields
    allure.attach("expected", repr(expected))
    _, obj = klass(attrs)
    content = get_content(obj)
    allure.attach("content", repr(content))
    assert_that(content, equal_to(expected))


@allure.feature("Serialization")
@pytest.mark.parametrize("klass", CLASSES[1:],
                         ids=[x.__name__ for x in CLASSES[1:]])
def test_restore_content(klass, simple_class_fields):
    allure.attach("attributes", repr(simple_class_fields))
    cls, expected = klass(simple_class_fields)
    obj = cls.__new__(cls)
    restore_content(obj, simple_class_fields)
    assert_that(obj, equal_to(expected))


@allure.feature("Serialization")
@pytest.mark.parametrize("klass", CLASSES[1:],
                         ids=[x.__name__ for x in CLASSES[1:]])
@pytest.mark.parametrize("serializer", ["json", "msgpack"])
def test_serialization(klass, serializer, simple_class_fields):
    cls, obj = klass(simple_class_fields, Serializable(serializer))
    serialized = obj.serialize()
    allure.attach("serialized", repr(serialized))
    assert_that(obj, cls.deserialize(serialized))
