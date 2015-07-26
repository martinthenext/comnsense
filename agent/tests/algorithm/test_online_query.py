# encoding=utf-8
import pytest
import mock
import random
import string
import allure
import json
from hamcrest import *


from ..fixtures.excel import workbook, sheetname
from ..fixtures.strings import random_word, random_first_last_name
from ..fixtures.strings import random_address, random_number
from comnsense_agent.data import Event, Cell, Action
from comnsense_agent.algorithm.online_query import OnlineQuery


FIXTURES = [([next(random_word()) for _ in range(10)], next(random_number())),
            ([next(random_number()) for _ in range(10)], next(random_word())),
            ([next(random_address()) for _ in range(10)], next(random_word())),
            # min 20 points, see online_query.py#check
            ([next(random_first_last_name()) for _ in range(20)],
             next(random_word()))]


@allure.feature("Online Query")
@allure.story("Blank Column")
@pytest.mark.parametrize("values,wrong", FIXTURES)
def test_online_query_on_blank_sheet(workbook, sheetname, values, wrong):
    algorithm = OnlineQuery()
    context = mock.Mock()

    column = "A"
    event_count = len(values)

    def get_event(num, value):
        key = "$%s$%d" % (column, num)
        cells = [[Cell(key, value)]]
        prev_cells = [[Cell(key, "")]]
        event = Event(Event.Type.SheetChange, workbook,
                      sheetname, cells, prev_cells)
        allure.attach("event", event.serialize(),
                      type=allure.attach_type.JSON)
        return event

    def attach_stats():
        stats = algorithm.columns[column].stats
        state = algorithm.columns[column].state
        interval = algorithm.columns[column].interval
        allure.attach("points", str(stats.points))
        allure.attach("stats", json.dumps(stats.stats, indent=2),
                      allure.attach_type.JSON)
        allure.attach("state", str(state.value))
        allure.attach("interval", str(interval))

    for num, value in enumerate(values, 1):
        with allure.step("send event: %d: %s" % (num, value)):
            event = get_event(num, value)
            actions = algorithm.handle(event, context)
            attach_stats()

    with allure.step("send wrong event: %s" % wrong):
        event = get_event(event_count + 1, wrong)
        actions = algorithm.handle(event, context)
        attach_stats()
        assert_that(actions, has_length(1))
        action = actions[0]
        assert_that(action, instance_of(Action))
        allure.attach("action", action.serialize(),
                      allure.attach_type.JSON)

        cell = action.cells[0][0]
        assert_that(cell.color, 3)
