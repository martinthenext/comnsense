import allure
import pytest
import mock
from hamcrest import *

from ..fixtures.excel import workbook, sheetname
from ..fixtures.excel import sheet_change, range_response

from comnsense_agent.algorithm.string_formatter import StringFormatter
from comnsense_agent.data import Action, Event, Cell


FIXTURES = [(["079-922-11-22",
              "079-933-22-11",
              "079-912-99-63",
              "079-915-77-18"]),
            (["079-922-11-22",
              "079-933-22-11",
              "079-912-99-66",
              "079-915-77-88"]),
            (["079-912-12-34",
              "079-913-34-56",
              "079-914-78-90",
              "079-915-21-43"])]


@allure.feature("String Formatter")
@allure.story("Zurich Phone Numbers")
@pytest.mark.parametrize("phones", FIXTURES)
def test_string_formatter_zurich_phone_numbers(workbook, sheetname, phones):
    algorithm = StringFormatter()
    context = mock.Mock()

    def correct(phone):
        return "(+41) " + " ".join(phone.split("-"))

    with allure.step("user change first number"):
        first = phones[0]
        event = next(sheet_change(workbook, sheetname, "$A$1",
                                  correct(first), first))
        allure.attach("event", event.serialize(), allure.attach_type.JSON)
        actions = algorithm.handle(event, context)
        assert_that(actions, is_(none()))

    with allure.step("user change next number"):
        second = phones[1]
        event = next(sheet_change(workbook, sheetname, "$A$2",
                                  correct(second), second))
        allure.attach("event", event.serialize(), allure.attach_type.JSON)
        actions = algorithm.handle(event, context)
        assert_that(actions, has_length(1))
        action = actions[0]
        allure.attach("action", action.serialize(), allure.attach_type.JSON)
        assert_that(action.range_name, equal_to("$A$3"))

    for cell, next_cell, phone, right_phone in zip(
             ["$A$3", "$A$4"], ["$A$4", "$A$5"],
             phones[2:], [correct(x) for x in phones[2:]]):
        with allure.step("next line range response: %s" % phone):
            event = next(range_response(workbook, sheetname, cell, phone))
            allure.attach("event", event.serialize(), allure.attach_type.JSON)
            actions = algorithm.handle(event, context)
            assert_that(actions, has_length(2))
            change_action, request_action = actions
            allure.attach(
                "change action", change_action.serialize(),
                allure.attach_type.JSON)
            allure.attach(
                "request action", request_action.serialize(),
                allure.attach_type.JSON)
            assert_that(change_action.cells[0][0].key, equal_to(cell))
            assert_that(change_action.cells[0][0].value, equal_to(right_phone))
            assert_that(request_action.range_name, equal_to(next_cell))

    with allure.step("blank line"):
        event = next(range_response(workbook, sheetname, "$A$5", ""))
        allure.attach("event", event.serialize(), allure.attach_type.JSON)
        actions = algorithm.handle(event, context)
        assert_that(actions, is_(none()))


@allure.feature("String Formatter")
@allure.story("Zurich Phone Numbers - Reversed")
@pytest.mark.parametrize("phones", FIXTURES)
def test_string_formatter_zurich_phone_numbers_reversed(
        workbook, sheetname, phones):
    algorithm = StringFormatter()
    context = mock.Mock()

    def correct(phone):
        return "(+41) " + " ".join(phone.split("-"))

    with allure.step("user change first number"):
        first = phones[0]
        event = next(sheet_change(workbook, sheetname, "$A$4",
                                  correct(first), first))
        allure.attach("event", event.serialize(), allure.attach_type.JSON)
        actions = algorithm.handle(event, context)
        assert_that(actions, is_(none()))

    with allure.step("user change next number"):
        second = phones[1]
        event = next(sheet_change(workbook, sheetname, "$A$3",
                                  correct(second), second))
        allure.attach("event", event.serialize(), allure.attach_type.JSON)
        actions = algorithm.handle(event, context)
        assert_that(actions, has_length(1))
        action = actions[0]
        allure.attach("action", action.serialize(), allure.attach_type.JSON)
        assert_that(action.range_name, equal_to("$A$2"))

    for cell, next_cell, phone, right_phone in zip(
             ["$A$2", "$A$1"], ["$A$1", None],
             phones[2:], [correct(x) for x in phones[2:]]):
        with allure.step("next line range response: %s" % phone):
            event = next(range_response(workbook, sheetname, cell, phone))
            allure.attach("event", event.serialize(), allure.attach_type.JSON)
            actions = algorithm.handle(event, context)
            if next_cell is None:
                assert_that(actions, has_length(1))
                change_action = actions[0]
                request_action = None
            else:
                assert_that(actions, has_length(2))
                change_action, request_action = actions
            allure.attach(
                "change action", change_action.serialize(),
                allure.attach_type.JSON)
            assert_that(change_action.cells[0][0].key, equal_to(cell))
            assert_that(change_action.cells[0][0].value, equal_to(right_phone))
            if request_action:
                allure.attach(
                    "request action", request_action.serialize(),
                    allure.attach_type.JSON)
                assert_that(request_action.range_name, equal_to(next_cell))
