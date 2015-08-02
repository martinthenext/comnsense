# coding=utf-8
import allure
import pytest
from hamcrest import *

from ..fixtures.excel import workbook as workbook_id
from .workbook import Workbook
from comnsense_agent.data import Cell

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
