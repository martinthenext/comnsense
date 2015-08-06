import pytest
import allure
from hamcrest import *
import json


from ..fixtures.excel import workbook, sheetname
from ..fixtures.strings import random_string

from comnsense_agent.data import Event, Action
from comnsense_agent.data import Cell
from comnsense_agent.data.data import Data


@allure.feature("Data")
def test_action_no_type():
    with pytest.raises(Data.ValidationError):
        Action(None, None, None, None)


@allure.feature("Data")
@pytest.mark.parametrize("type", Action.Type.__members__.values())
def test_action_no_workbook(type):
    with pytest.raises(Data.ValidationError):
        Action(type, None, None, None)


@allure.feature("Data")
@pytest.mark.parametrize("type", Action.Type.__members__.values())
def test_action_no_sheet(type, workbook):
    with pytest.raises(Data.ValidationError):
        Action(type, workbook, None, None)


@allure.feature("Data")
@pytest.mark.parametrize("type", Action.Type.__members__.values())
def test_action_no_content(type, workbook, sheetname):
    with pytest.raises(Data.ValidationError):
        Action(type, workbook, sheetname, None)


@allure.feature("Data")
@pytest.mark.parametrize("content", [None, 0, [], 10, 1.0, "$A$1:$A$2"])
def test_action_change_cell_bad_content(workbook, sheetname, content):
    with pytest.raises(Data.ValidationError):
        Action(Action.Type.ChangeCell, workbook, sheetname, content)


FIXTURES = [[[Cell("$A$1", "")]],
            [[Cell("$A$1", "")], [Cell("$A$2", "")]],
            [[Cell("$A$1", ""), Cell("$B$1", "")]]]


@allure.feature("Data")
@pytest.mark.parametrize("content", FIXTURES)
def test_action_change_cell(workbook, sheetname, content):
    action = Action(Action.Type.ChangeCell, workbook, sheetname, content)
    assert_that(action.type, equal_to(Action.Type.ChangeCell))
    assert_that(action.workbook, equal_to(workbook))
    assert_that(action.sheet, equal_to(sheetname))
    assert_that(action.cells, equal_to(content))
    assert_that(action.range_name, is_(none()))
    assert_that(action.flags, equal_to(Action.Flags.NoFlags))


@allure.feature("Data")
@pytest.mark.parametrize("content", FIXTURES)
def test_action_change_cell_helper(workbook, sheetname, content):
    expected = Action(Action.Type.ChangeCell, workbook, sheetname, content)
    action = Action.change(workbook, sheetname, content)
    assert_that(action, equal_to(expected))


@allure.feature("Data")
@pytest.mark.parametrize("content", FIXTURES)
@pytest.mark.parametrize("event_type", [Event.Type.RangeResponse,
                                        Event.Type.SheetChange])
def test_action_change_cell_event_helper(workbook, sheetname,
                                         content, event_type):
    expected = Action(Action.Type.ChangeCell, workbook, sheetname, content)
    event = Event(event_type, workbook, sheetname, content)
    action = Action.change_from_event(event, content)
    assert_that(action, equal_to(expected))


@allure.feature("Data")
@pytest.mark.parametrize("content", FIXTURES)
def test_action_change_cell_serialization(workbook, sheetname, content):
    action = Action(Action.Type.ChangeCell, workbook, sheetname, content)
    serialized = action.serialize()
    allure.attach("action", serialized, allure.attach_type.JSON)
    deserialized = Action.deserialize(serialized)
    assert_that(action, equal_to(deserialized))
    dct = json.loads(serialized)
    assert_that(dct, has_key("cells"))
    assert_that(dct, is_not(has_key("rangeName")))
    assert_that(dct, is_not(has_key("flags")))


@allure.feature("Data")
@pytest.mark.parametrize("content", [None, 0, [], 10, 1.0, [[]], ""])
def test_action_request_bad_content(workbook, sheetname, content):
    with pytest.raises(Data.ValidationError):
        Action(Action.Type.RangeRequest, workbook, sheetname, content)


FIXTURES = ["$A$1", "$A$1:$C$5"]


@allure.feature("Data")
@pytest.mark.parametrize("content", FIXTURES)
@pytest.mark.parametrize("flags", [-1, 16, 100])
def test_action_request_bad_flags(workbook, sheetname, content, flags):
    with pytest.raises(Data.ValidationError):
        Action(Action.Type.RangeRequest, workbook, sheetname, content, flags)


@allure.feature("Data")
@pytest.mark.parametrize("content", FIXTURES)
@pytest.mark.parametrize("flags", [None, 0, "", []])
def test_action_request_no_flags(workbook, sheetname, content, flags):
    action = Action(
        Action.Type.RangeRequest, workbook, sheetname, content, flags)
    assert_that(action.flags, equal_to(Action.Flags.NoFlags))


FLAGS = range(0, 15) + Action.Flags.__members__.values()


@allure.feature("Data")
@pytest.mark.parametrize("content", FIXTURES)
@pytest.mark.parametrize("flags", FLAGS)
def test_action_request(workbook, sheetname, content, flags):
    action = Action(
        Action.Type.RangeRequest, workbook, sheetname, content, flags)
    assert_that(action.type, equal_to(Action.Type.RangeRequest))
    assert_that(action.workbook, equal_to(workbook))
    assert_that(action.sheet, equal_to(sheetname))
    assert_that(action.range_name, equal_to(content))
    assert_that(action.cells, is_(none()))
    assert_that(action.flags, equal_to(flags))


@allure.feature("Data")
@pytest.mark.parametrize("content", FIXTURES)
@pytest.mark.parametrize("flags", FLAGS)
def test_action_request_helper(workbook, sheetname, content, flags):
    expected = Action(
        Action.Type.RangeRequest, workbook, sheetname, content, flags)
    action = Action.request(workbook, sheetname, content, flags)
    assert_that(action, equal_to(expected))


@allure.feature("Data")
@pytest.mark.parametrize("content", FIXTURES)
@pytest.mark.parametrize("flags", FLAGS)
@pytest.mark.parametrize("event_type", [Event.Type.RangeResponse,
                                        Event.Type.SheetChange])
def test_action_request_event_helper(workbook, sheetname, content,
                                     flags, event_type):
    expected = Action(
        Action.Type.RangeRequest, workbook, sheetname, content, flags)
    event = Event(event_type, workbook, sheetname, content)
    action = Action.request_from_event(event, content, flags)
    assert_that(action, equal_to(expected))


@allure.feature("Data")
@pytest.mark.parametrize("content", FIXTURES)
@pytest.mark.parametrize("flags", FLAGS)
def test_action_request_serialization(workbook, sheetname, content, flags):
    action = Action(
        Action.Type.RangeRequest, workbook, sheetname, content, flags)
    serialized = action.serialize()
    allure.attach("action", serialized, allure.attach_type.JSON)
    deserialized = Action.deserialize(serialized)
    assert_that(action, equal_to(deserialized))
    dct = json.loads(serialized)
    assert_that(dct, is_not(has_key("cells")))
    assert_that(dct, has_key("rangeName"))
    if action.flags != Action.Flags.NoFlags:
        assert_that(dct, has_key("flags"))
    else:
        assert_that(dct, is_not(has_key("flags")))


FIXTURES = [(Action.Type.ChangeCell, [[Cell("$A$1", next(random_string()))]]),
            (Action.Type.RangeRequest, "$A$3:$A$6")]


@allure.feature("Data")
@pytest.mark.parametrize("action_type, content", FIXTURES)
def test_action_repr(workbook, sheetname, action_type, content):
    action = Action(action_type, workbook, sheetname, content)
    assert_that(len(repr(action)), greater_than(0))
    assert_that(len(str(action)), greater_than(0))
