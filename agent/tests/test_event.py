# coding=utf-8
import unittest
import pytest
import random
import string
import json

from .common import get_random_cell_key

from comnsense_agent.data import Event, EventError
from comnsense_agent.data import Cell, Border


class TestEvent(unittest.TestCase):
    def test_normal(self):
        type = random.choice(Event.Type.__members__.values())
        workbook = "".join(random.sample(string.ascii_letters, 10))
        sheet = "".join(random.sample(string.ascii_letters, 10))
        cells = [[Cell(get_random_cell_key(), u"траливали")],
                 [Cell(get_random_cell_key(), u"дили-дили\"")]]
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

    def test_deserialization(self):
        fixture = """
        {"type" : 0,
         "workbook" : "f1f2d913-8de3-49b6-8993-f6b026686cda",
         "sheet": "\xd0\xb2\xd0\xb0\xd1\x81\xd0\xb8\xd0\xbb\xd0\xb8\xd0\xb9",
         "cells": [
           [{"key": "$B$3",
             "value":"33",
             "color":3,
             "font": "Times New Roman",
             "borders": {"right": [4, 1],
                         "bottom" : [-4138, 1]
                        },
             "fontstyle": 5}
           ]
         ]
        }"""
        event = Event.deserialize(fixture)
        self.assertEquals(event.type, Event.Type.WorkbookOpen)
        self.assertEquals(event.workbook,
                          "f1f2d913-8de3-49b6-8993-f6b026686cda")
        self.assertEquals(event.sheet, u"василий")
        self.assertEquals(len(event.cells), 1)
        self.assertEquals(len(event.cells[0]), 1)
        cell = event.cells[0][0]
        self.assertEquals(cell.key, "$B$3")
        self.assertEquals(cell.value, "33")
        self.assertEquals(cell.color, 3)
        self.assertTrue(cell.bold)
        self.assertFalse(cell.italic)
        self.assertTrue(cell.underline)
        self.assertEquals(cell.font, "Times New Roman")
        self.assertEquals(cell.borders.right.weight,
                          Border.Weight.xlThick)
        self.assertEquals(cell.borders.right.linestyle,
                          Border.LineStyle.xlContinuous)
        self.assertEquals(cell.borders.bottom.weight,
                          Border.Weight.xlMedium)
        self.assertEquals(cell.borders.bottom.linestyle,
                          Border.LineStyle.xlContinuous)
