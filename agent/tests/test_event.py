# coding=utf-8
import unittest
import pytest
import random
import string
import json


from comnsense_agent.data import Event, EventError


class TestEvent(unittest.TestCase):
    def test_normal(self):
        type = random.choice(Event.Type.__members__.values())
        workbook = "".join(random.sample(string.ascii_letters, 10))
        sheet = "".join(random.sample(string.ascii_letters, 10))
        cells = [[u"A1", u"траливали"], [u"A2", u"дили-дили\""]]
        event = Event(type, workbook, sheet, cells)
        self.assertEquals(event.type, type)
        self.assertEquals(event.workbook, workbook)
        self.assertEquals(event.sheet, sheet)
        self.assertEquals(event.cells, cells)
        data = event.serialize()
        another = Event.deserialize(data)
        self.assertEquals(event.type, another.type)
        self.assertEquals(event.workbook, another.workbook)
        self.assertEquals(event.sheet, another.sheet)
        self.assertEquals(event.cells, another.cells)

    def test_without_cells(self):
        type = random.choice(Event.Type.__members__.values())
        workbook = "".join(random.sample(string.ascii_letters, 10))
        sheet = "".join(random.sample(string.ascii_letters, 10))
        event = Event(type, workbook, sheet)
        self.assertEquals(event.type, type)
        self.assertEquals(event.workbook, workbook)
        self.assertEquals(event.sheet, sheet)
        self.assertEquals(event.cells, [])
        data = event.serialize()
        another = Event.deserialize(data)
        self.assertEquals(event.type, another.type)
        self.assertEquals(event.workbook, another.workbook)
        self.assertEquals(event.sheet, another.sheet)
        self.assertEquals(event.cells, another.cells)

    def test_without_sheet_and_cells(self):
        type = random.choice(Event.Type.__members__.values())
        workbook = "".join(random.sample(string.ascii_letters, 10))
        event = Event(type, workbook)
        self.assertEquals(event.type, type)
        self.assertEquals(event.workbook, workbook)
        self.assertEquals(event.sheet, None)
        self.assertEquals(event.cells, [])
        data = event.serialize()
        another = Event.deserialize(data)
        self.assertEquals(event.type, another.type)
        self.assertEquals(event.workbook, another.workbook)
        self.assertEquals(event.sheet, another.sheet)
        self.assertEquals(event.cells, another.cells)

    def test_bad_type(self):
        workbook = "".join(random.sample(string.ascii_letters, 10))
        type = random.choice(range(10))
        with pytest.raises(EventError):
            Event(type, workbook)

    def test_bad_workbook(self):
        type = random.choice(range(10))
        with pytest.raises(EventError):
            Event(type)

    def test_serialization(self):
        fixture = """
        {"type": 0,
         "workbook": "dwaeqdasda",
         "sheet": 1,
         "cells": [[{"A1": "asdadad"}]]
        }
        """
        event = Event.deserialize(fixture).serialize()
        self.assertEquals(json.loads(fixture), json.loads(event))
