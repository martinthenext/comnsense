# coding=utf-8
import allure
import pytest
import itertools
from hamcrest import *

from ..fixtures.excel import workbook as workbook_id
from .workbook import Workbook
from .scenario import Scenario
from comnsense_agent.data import Cell, Event, Action

SHEET = """
  A  |        B     |    C
------------------------------
Name | City         |  Phone
John | NY           | 1234567
Mike | LA:color::3  | 2345678
Jim  | Boston       | 3456789
==============================
Contacts
"""


@allure.feature("Testing")
def test_workbook_init(workbook_id):
    wb = Workbook(workbook_id, SHEET)
    assert_that(wb.sheets(), equal_to(["Contacts"]))
    assert_that(wb.identity, workbook_id)
    assert_that(wb.columns("Contacts"), equal_to(["A", "B", "C"]))


@allure.feature("Testing")
def test_workbook_serialization(workbook_id):
    wb = Workbook(workbook_id, SHEET)
    serialized = wb.serialize("Contacts")
    allure.attach("serialized", serialized)
    another = Workbook(workbook_id, serialized)
    assert_that(another, equal_to(wb))


@allure.feature("Testing")
def test_workbook_get(workbook_id):
    wb = Workbook(workbook_id, SHEET)
    assert_that(wb.get("Contacts", "$B$2"),
                equal_to(Cell("$B$2", "NY")))
    assert_that(wb.get("Contacts", "$B$3"),
                equal_to(Cell("$B$3", "LA", color=3)))


@allure.feature("Testing")
def test_workbook_put(workbook_id):
    wb = Workbook(workbook_id, SHEET)
    cell = Cell("$D$5", "test", color=5)
    wb.put("Contacts", cell)
    assert_that(wb.get("Contacts", "$D$5"),
                equal_to(cell))
    assert_that(wb.get("Contacts", "$B$5"),
                equal_to(Cell("$B$5", "")))
    cell = Cell("$A$3", u"Василий")
    wb.put("Contacts", cell)
    assert_that(wb.get("Contacts", "$A$3"),
                equal_to(cell))
    serialized = wb.serialize("Contacts")
    allure.attach("serialized", serialized)


@allure.feature("Testing")
def test_scenario_simple(workbook_id):
    types = [Event.Type.WorkbookOpen,
             Event.Type.SheetChange,
             Event.Type.SheetChange,
             Event.Type.WorkbookBeforeClose]
    wb = Workbook(workbook_id, SHEET)
    sc = Scenario(wb)

    expected = Workbook(workbook_id, u"""
      A     |        B     |    C
    ---------------------------------
    Name    | City         |  Phone
    Василий | Москва       | 1234567
    Mike    | LA:color::3  | 2345678
    Jim     | Boston       | 3456789
    =================================
    Contacts
    """)

    sc.open(comment="open workbook")
    sc.change("Contacts", "$A$2", u"Василий", comment="change name")
    sc.change("Contacts", "$B$2", u"Москва", comment="change city")
    sc.close(comment="close workbook")
    for event, type in itertools.izip(sc, types):
        assert_that(event.type, equal_to(type))

    assert_that(sc.workbook, equal_to(expected))


@allure.feature("Testing")
def test_scenario_change_cell_action(workbook_id):
    wb = Workbook(workbook_id, SHEET)
    sc = Scenario(wb)

    expected = Workbook(workbook_id, u"""
      A     |        B     |    C
    ---------------------------------
    Name    | City         |  Phone
    Василий | Москва       | 1234567
    Mike    | LA:color::3  | 2345678
    Jim     | Boston       | 3456789
    =================================
    Contacts
    """)

    sc.open(comment="open workbook")
    sc.change("Contacts", "$A$2", u"Василий", comment="change name")
    sc.close(comment="close workbook")

    for event in sc:
        if event.type == Event.Type.SheetChange:
            action = Action.change_from_event(
                event, [[Cell("$B$2", u"Москва")]])
            sc.apply(action)

    assert_that(sc.workbook, equal_to(expected))


@allure.feature("Testing")
def test_scenario_range_request_action(workbook_id):
    wb = Workbook(workbook_id, SHEET)
    sc = Scenario(wb)

    sc.open(comment="open workbook")
    sc.change("Contacts", "$A$2", u"Василий", comment="change name")
    sc.close(comment="close workbook")

    for event in sc:
        if event.type == Event.Type.SheetChange:
            action = Action.request_from_event(
                event, "$C$2:$C$4")
            answer = sc.apply(action)
            assert_that(answer.cells, equal_to([[Cell("$C$2", "1234567")],
                                                [Cell("$C$3", "2345678")],
                                                [Cell("$C$4", "3456789")]]))
