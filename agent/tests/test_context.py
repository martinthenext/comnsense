import pytest
import unittest
import random
import string
import mock
import allure
import collections
from hamcrest import *

from .fixtures.excel import workbook, sheetname

from comnsense_agent.context import Context
from comnsense_agent.algorithm.event_handler import EventHandler


@allure.feature("Context")
def test_context_workbook(workbook):
    context = Context()
    assert_that(context.workbook, is_(none()))
    context.workbook = workbook
    assert_that(context.workbook, equal_to(workbook))
    with pytest.raises(AttributeError):
        context.workbook = workbook


@allure.feature("Context")
def test_context_no_sheets(workbook):
    context = Context()
    context.workbook = workbook
    assert_that(context.sheets, has_length(0))


@allure.feature("Context")
def test_context_new_sheet(workbook, sheetname):
    context = Context()
    context.workbook = workbook
    handlers = context.handlers(sheetname)
    assert_that(context.sheets, has_item(sheetname))
    assert_that(handlers, instance_of(collections.Sequence))
    for handler in handlers:
        assert_that(handler, instance_of(EventHandler))


@allure.feature("Context")
def test_context_method_lookup(workbook, sheetname):
    context = Context()
    context.workbook = workbook
    method = context.lookup(sheetname).get_header
    assert_that(method, instance_of(collections.Callable))
    with pytest.raises(AttributeError):
        context.lookup(sheetname).unknown
