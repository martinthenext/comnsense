# encoding=utf-8
import allure
import json
import mock
import pytest
import random
import string
from hamcrest import *


from ..fixtures.excel import workbook, sheetname, sheet_change
from ..fixtures.excel import random_sheet_change, random_range_response
from ..fixtures.strings import random_word, random_first_last_name
from ..fixtures.strings import random_address, random_number
from comnsense_agent.data import Event, Cell, Action
from comnsense_agent.algorithm.error_detector import ErrorDetector


def attach_stats(algorithm, column):
    stats = algorithm.columns[column].stats
    state = algorithm.columns[column].state
    interval = algorithm.columns[column].interval
    allure.attach("points", str(stats.points))
    allure.attach("stats", json.dumps(stats.stats, indent=2),
                  allure.attach_type.JSON)
    allure.attach("state", str(state.value))
    allure.attach("interval", str(interval))


def get_context_without_header():
    context = mock.Mock()
    handler = mock.Mock()
    context.lookup.return_value = handler
    handler.get_header.return_value = None
    return context


def get_context_empty_header():
    context = mock.Mock()
    handler = mock.Mock()
    context.lookup.return_value = handler
    handler.get_header.return_value = []
    handler.get_header_rows.return_value = set([])
    handler.get_header_columns.return_value = set([])
    return context


def get_context_with_header(column):
    context = mock.Mock()
    handler = mock.Mock()
    context.lookup.return_value = handler
    handler.get_header.return_value = \
        [Cell("$%s$1" % column, next(random_word()))]
    handler.get_header_rows.return_value = set(["1"])
    handler.get_header_columns.return_value = set([column])
    return context


@allure.feature("Error Detector")
@allure.story("Without Header")
@pytest.mark.parametrize("event",
                         [random_range_response,
                          random_sheet_change],
                         ids=["RangeResponse", "SheetChange"])
@pytest.mark.parametrize("context",
                         [get_context_without_header,
                          get_context_empty_header],
                         ids=["HeaderNotYetFound", "EmptyHeader"])
def test_online_query_without_header(workbook, sheetname, event, context):
    algorithm = ErrorDetector()
    context = context()
    event = next(event(workbook, sheetname))
    allure.attach("event", event.serialize(), type=allure.attach_type.JSON)

    actions = algorithm.handle(event, context)
    assert_that(actions, is_([]))


FIXTURES = [([next(random_word()) for _ in range(10)], next(random_number())),
            ([next(random_number()) for _ in range(10)], next(random_word())),
            ([next(random_address()) for _ in range(10)], next(random_word())),
            # min 20 points, see online_query.py#check
            ([next(random_first_last_name()) for _ in range(20)],
             next(random_word()))]


@allure.feature("Error Detector")
@allure.story("Append Values To Blank Column")
@pytest.mark.parametrize("values,wrong", FIXTURES)
def test_online_query_without_response(workbook, sheetname, values, wrong):
    algorithm = ErrorDetector()
    column = "A"
    min_row = 2
    rows_in_request = 10
    context = get_context_with_header(column)
    event_count = len(values)

    def get_event(num, value):
        key = "$%s$%d" % (column, num)
        event = next(sheet_change(workbook, sheetname, key, value))
        allure.attach("event", event.serialize(),
                      type=allure.attach_type.JSON)
        return event

    for num, value in enumerate(values, min_row):
        with allure.step("send event: %d: %s" % (num, value)):
            event = get_event(num, value)
            actions = algorithm.handle(event, context)
            attach_stats(algorithm, column)
            if num < rows_in_request:
                assert_that(actions, has_length(1))
                action = actions[0]
                assert_that(action, instance_of(Action))
                allure.attach("action", action.serialize(),
                              allure.attach_type.JSON)
                assert_that(
                    action.range_name,
                    equal_to("$%s$%d:$%s$%d" %
                             (column, num + 1, column, num + rows_in_request)))

    with allure.step("send wrong event: %s" % wrong):
        event = get_event(event_count + min_row, wrong)
        actions = algorithm.handle(event, context)
        attach_stats(algorithm, column)
        assert_that(actions, has_length(1))
        action = actions[0]
        assert_that(action, instance_of(Action))
        allure.attach("action", action.serialize(),
                      allure.attach_type.JSON)

        cell = action.cells[0][0]
        assert_that(cell.color, equal_to(3))


@allure.feature("Error Detector")
@allure.story("Append Value To Column With Data")
@pytest.mark.parametrize("values,wrong", FIXTURES)
def test_online_query_with_response(workbook, sheetname, values, wrong):
    algorithm = ErrorDetector()

    column = "A"
    min_row = 2
    rows_in_request = 10
    context = get_context_with_header(column)
    event_count = len(values)

    def get_change(num, value, prev_value=""):
        key = "$%s$%d" % (column, num)
        event = next(sheet_change(workbook, sheetname, key, value, prev_value))
        allure.attach("event", event.serialize(),
                      type=allure.attach_type.JSON)
        return event

    def get_response(num, values, count):
        cells = []
        for i, value in enumerate(values[:count], num):
            key = "$%s$%d" % (column, i)
            cells.append([Cell(key, value)])
        for i in range(num + len(values), num + count):
            key = "$%s$%d" % (column, i)
            cells.append([Cell(key, "")])
        event = Event(Event.Type.RangeResponse,
                      workbook, sheetname, cells)
        allure.attach("event", event.serialize(),
                      type=allure.attach_type.JSON)
        return event

    # TODO see issue #11
    row = random.randint(min_row, len(values[:rows_in_request]) - 1)
    with allure.step("first event: %d: %s" % (row, values[row])):
        event = get_change(row + 1, values[row])
        actions = algorithm.handle(event, context)
        attach_stats(algorithm, column)
        assert_that(actions, has_length(1))
        action = actions[0]
        assert_that(action, instance_of(Action))
        allure.attach("action", action.serialize(),
                      allure.attach_type.JSON)
        expected = "$%s$%d:$%s$%s" % (column, min_row,
                                      column, min_row + rows_in_request - 1)
        assert_that(action.range_name, equal_to(expected))

    with allure.step("first action response"):
        event = get_response(min_row, values, rows_in_request)
        actions = algorithm.handle(event, context)
        attach_stats(algorithm, column)
        assert_that(actions, has_length(1))
        action = actions[0]
        assert_that(action, instance_of(Action))
        allure.attach("action", action.serialize(),
                      allure.attach_type.JSON)
        expected = "$%s$%d:$%s$%s" % (
            column, min_row + rows_in_request,
            column, min_row + rows_in_request * 2 - 1)
        assert_that(action.range_name, equal_to(expected))

    with allure.step("second action response"):
        event = get_response(min_row + rows_in_request + 1,
                             values[rows_in_request:], rows_in_request)
        actions = algorithm.handle(event, context)
        attach_stats(algorithm, column)
        assert_that(actions, has_length(0))

    with allure.step("correct value: %d: %s -> %s" %
                     (row, values[row], values[row - 1])):
        event = get_change(row + 1, values[row - 1], values[row])
        actions = algorithm.handle(event, context)
        attach_stats(algorithm, column)
        assert_that(actions, has_length(0))

    with allure.step("wrong value %d: %s" %
                     (len(values) + min_row + 1, wrong)):
        event = get_change(len(values) + min_row + 1, wrong)
        actions = algorithm.handle(event, context)
        attach_stats(algorithm, column)
        assert_that(actions, has_length(1))
        action = actions[0]
        assert_that(action, instance_of(Action))
        allure.attach("action", action.serialize(),
                      allure.attach_type.JSON)
        assert_that(action.cells[0][0].color, equal_to(3))


@allure.feature("Error Detector")
@allure.story("Change Incorrect Value")
@pytest.mark.parametrize("values,wrong", FIXTURES)
def test_online_query_change_value(workbook, sheetname, values, wrong):
    algorithm = ErrorDetector()
    column = "A"
    min_row = 2
    rows_in_request = 10
    context = get_context_with_header(column)
    event_count = len(values)

    def get_event(num, value, prev_value=""):
        key = "$%s$%d" % (column, num)
        event = next(sheet_change(workbook, sheetname, key, value, prev_value))
        allure.attach("event", event.serialize(),
                      type=allure.attach_type.JSON)
        return event

    for num, value in enumerate(values, min_row):
        with allure.step("send event: %d: %s" % (num, value)):
            event = get_event(num, value)
            actions = algorithm.handle(event, context)
            attach_stats(algorithm, column)

    with allure.step("send wrong event: %s" % wrong):
        event = get_event(event_count + min_row, wrong)
        actions = algorithm.handle(event, context)
        attach_stats(algorithm, column)
        assert_that(actions, has_length(1))
        action = actions[0]
        assert_that(action, instance_of(Action))
        allure.attach("action", action.serialize(),
                      allure.attach_type.JSON)
        cell = action.cells[0][0]
        assert_that(cell.color, equal_to(3))

    correct = random.choice(values)
    with allure.step("correct event: %s -> %s" % (wrong, correct)):
        event = get_event(event_count + min_row, correct, wrong)
        actions = algorithm.handle(event, context)
        attach_stats(algorithm, column)
        assert_that(actions, has_length(1))
        action = actions[0]
        assert_that(action, instance_of(Action))
        allure.attach("action", action.serialize(),
                      allure.attach_type.JSON)
        cell = action.cells[0][0]
        assert_that(cell.color, equal_to(0))
