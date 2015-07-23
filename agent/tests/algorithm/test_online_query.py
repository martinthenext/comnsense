# encoding=utf-8
import pytest
import mock
import random
import string
import allure
import json
from hamcrest import *


from ..fixtures.excel import workbook, sheetname
from comnsense_agent.data import Event, Cell, Action
from comnsense_agent.algorithm.laptev import OnlineQuery


def get_random_lowercase_ascii_string():
    max_length = 10
    min_length = 1
    length = random.randint(min_length, max_length)
    result = "".join(random.sample(string.ascii_lowercase, length))
    return result


@allure.feature("Online Query")
def test_online_query_on_blank_sheet(workbook, sheetname):
    """
        Case:
            creating column with english letters on empty sheet
    """
    algorithm = OnlineQuery()
    context = mock.Mock()

    column = "A"
    event_count = 10

    def get_event(num, value=None):
        key = "$%s$%d" % (column, num)
        if value is None:
            value = get_random_lowercase_ascii_string()
        cells = [[Cell(key, value)]]
        prev_cells = [[Cell(key, "")]]
        event = Event(Event.Type.SheetChange, workbook,
                      sheetname, cells, prev_cells)
        allure.attach("event", event.serialize(),
                      type=allure.attach_type.JSON)
        return event

    def get_stats():
        n_points, stats = algorithm.get_stats(column)
        allure.attach("n_points", str(n_points))
        allure.attach("stats", json.dumps(stats, indent=2),
                      allure.attach_type.JSON)
        return n_points, stats

    for num in range(1, event_count + 1):
        with allure.step("send event: %d" % num):
            event = get_event(num)
            actions = algorithm.handle(event, context)
            n_points, stats = get_stats()
            assert_that(actions, none())

    with allure.step("send wrong event"):
        event = get_event(event_count + 1, "1")
        actions = algorithm.handle(event, context)
        n_points, stats = get_stats()
        assert_that(actions, has_length(1))
        action = actions[0]
        assert_that(action, instance_of(Action))
        allure.attach("action", action.serialize(),
                      allure.attach_type.JSON)

        cell = action.cells[0][0]
        assert_that(cell.color, 3)
