import pytest
import allure
from hamcrest import *

from ..fixtures.classes import NewStyleClass

from comnsense_agent.algorithm.event_handler import EventHandler, publicmethod
from comnsense_agent.algorithm.event_handler import PublicMethodLookup


def test_event_handler_abstract_method():
    klass, obj = NewStyleClass({}, EventHandler)
    with pytest.raises(NotImplementedError):
        obj.handle("event", "context")


def test_event_handler_provides():
    klass, _ = NewStyleClass({}, EventHandler)
    klass.method = publicmethod(lambda x: x)
    klass.another = (lambda x: x)
    obj = klass()
    assert_that(obj.provides, has_item("method"))
    assert_that(klass.provides, has_item("method"))
    assert_that(obj.provides, is_not(has_item("another")))
    assert_that(klass.provides, is_not(has_item("another")))


def test_event_handler_lookup():
    one, _ = NewStyleClass({}, EventHandler)
    another, _ = NewStyleClass({}, EventHandler)
    one.one = publicmethod(lambda x: "one.one")
    another.one = publicmethod(lambda x: "another.one")
    another.another = publicmethod(lambda x: "another.another")
    lookup = PublicMethodLookup([one(), another()])
    assert_that(lookup.one(), equal_to("one.one"))
    assert_that(lookup.another(), equal_to("another.another"))
    with pytest.raises(AttributeError):
        lookup.unknown()
