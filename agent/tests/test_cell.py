import unittest
import pytest
import random
import string


from comnsense_agent.data import Border
from comnsense_agent.data import Borders
from comnsense_agent.data import Cell

from .common import *


class TestBorder(unittest.TestCase):
    def test_enum_initialization(self):
        linestyle = get_random_linestyle()
        weight = get_random_weight()
        border = Border(weight, linestyle)
        self.assertEquals(border.linestyle, linestyle)
        self.assertEquals(border.weight, weight)

    def test_int_initialization(self):
        linestyle = get_random_linestyle()
        weight = get_random_weight()
        border = Border(weight.value, linestyle.value)
        self.assertEquals(border.linestyle, linestyle)
        self.assertEquals(border.weight, weight)

    def test_weight(self):
        linestyle = get_random_linestyle()
        weight = get_random_weight()
        border = Border(weight, linestyle)
        weight = get_random_weight()
        border.weight = weight.value
        self.assertEquals(border.weight, weight)

    def test_linestyle(self):
        linestyle = get_random_linestyle()
        weight = get_random_weight()
        border = Border(weight, linestyle)
        linestyle = get_random_linestyle()
        border.linestyle = linestyle.value
        self.assertEquals(border.linestyle, linestyle)

    def test_serialization(self):
        linestyle = get_random_linestyle()
        weight = get_random_weight()
        border = Border(weight, linestyle)
        self.assertEquals(
            border.to_primitive(),
            [weight.value, linestyle.value])

    def test_deserialization(self):
        linestyle = get_random_linestyle()
        weight = get_random_weight()
        obj = [weight.value, linestyle.value]
        border = Border.from_primitive(obj)
        self.assertEquals(border.linestyle, linestyle)
        self.assertEquals(border.weight, weight)

    def test_invalid_weight(self):
        linestyle = get_random_linestyle()
        weight = get_random_weight()
        invalid_weight = 1000000
        with pytest.raises(ValueError):
            Border(invalid_weight, linestyle)
        border = Border(weight, linestyle)
        with pytest.raises(ValueError):
            border.weight = invalid_weight

    def test_invalid_linestyle(self):
        linestyle = get_random_linestyle()
        weight = get_random_weight()
        invalid_linestyle = 1000000
        with pytest.raises(ValueError):
            Border(weight, invalid_linestyle)
        border = Border(weight, linestyle)
        with pytest.raises(ValueError):
            border.linestyle = invalid_linestyle


class TestBorders(unittest.TestCase):
    def test_trivial_serialization(self):
        borders = Borders()
        self.assertEquals(borders.to_primitive(), None)

    def test_trivial_deserialization(self):
        borders = Borders.from_primitive(None)
        self.assertEquals(borders.top, None)
        self.assertEquals(borders.left, None)
        self.assertEquals(borders.bottom, None)
        self.assertEquals(borders.right, None)

    def test_single(self):
        side, other = get_random_border_side()
        border = get_random_border()
        original = {side: border.to_primitive()}
        borders = Borders.from_primitive(original)
        self.assertEquals(getattr(borders, side), border)
        for one in other:
            self.assertEquals(getattr(borders, one), None)
        self.assertEquals(borders.to_primitive(), original)


class TestCell(unittest.TestCase):
    def test_trivial(self):
        key = get_random_cell_key()
        value = random.choice(string.ascii_letters)
        original = {"key": key, "value": value}
        cell = Cell(key, value)
        self.assertEquals(key, cell.key)
        self.assertEquals(value, cell.value)
        obj = cell.to_primitive()
        self.assertEquals(obj, original)
        another = Cell.from_primitive(original)
        self.assertEquals(cell, another)

    def test_borders(self):
        key = get_random_cell_key()
        value = random.choice(string.ascii_letters)
        borders = get_random_borders()
        original = {
            "key": key,
            "value": value,
            "borders": borders.to_primitive()
        }
        cell = Cell(key, value, borders=borders)
        self.assertEquals(key, cell.key)
        self.assertEquals(value, cell.value)
        self.assertEquals(borders, cell.borders)
        obj = cell.to_primitive()
        self.assertEquals(obj, original)
        another = Cell.from_primitive(original)
        self.assertEquals(cell, another)

    def test_other(self):
        key = get_random_cell_key()
        value = random.choice(string.ascii_letters)
        borders = get_random_borders()
        color = random.choice(range(1, 10))
        fontstyle = random.choice(range(1, 5))
        font = random.choice(string.ascii_letters)
        original = {
            "key": key,
            "value": value,
            "borders": borders.to_primitive(),
            "color": color,
            "font": font,
            "fontstyle": fontstyle,
        }
        cell = Cell(key, value,
                    borders=borders, color=color,
                    font=font, fontstyle=fontstyle)
        self.assertEquals(key, cell.key)
        self.assertEquals(value, cell.value)
        self.assertEquals(borders, cell.borders)
        self.assertEquals(color, cell.color)
        self.assertEquals(font, cell.font)
        self.assertEquals(fontstyle, cell.fontstyle)
        obj = cell.to_primitive()
        self.assertEquals(obj, original)
        another = Cell.from_primitive(original)
        self.assertEquals(cell, another)

    def test_bold(self):
        key = get_random_cell_key()
        value = random.choice(string.ascii_letters)
        cell = Cell(key, value)
        self.assertFalse(cell.bold)
        cell.bold = True
        self.assertTrue(cell.bold)
        cell.bold = False
        self.assertFalse(cell.bold)

    def test_italic(self):
        key = get_random_cell_key()
        value = random.choice(string.ascii_letters)
        cell = Cell(key, value)
        self.assertFalse(cell.italic)
        cell.italic = True
        self.assertTrue(cell.italic)
        cell.italic = False
        self.assertFalse(cell.italic)

    def test_underline(self):
        key = get_random_cell_key()
        value = random.choice(string.ascii_letters)
        cell = Cell(key, value)
        self.assertFalse(cell.underline)
        cell.underline = True
        self.assertTrue(cell.underline)
        cell.underline = False
        self.assertFalse(cell.underline)

    def test_zero_fontstyle(self):
        key = get_random_cell_key()
        value = random.choice(string.ascii_letters)
        cell = Cell(key, value, fontstyle=0)
        another = Cell.from_primitive(cell.to_primitive())
        self.assertEquals(another.key, cell.key)
        self.assertEquals(another.value, cell.value)
        self.assertEquals(another.borders, cell.borders)
        self.assertEquals(another.color, cell.color)
        self.assertEquals(another.font, cell.font)
        self.assertEquals(another.fontstyle, cell.fontstyle)

    def test_zero_color(self):
        key = get_random_cell_key()
        value = random.choice(string.ascii_letters)
        cell = Cell(key, value, color=0)
        another = Cell.from_primitive(cell.to_primitive())
        self.assertEquals(another.key, cell.key)
        self.assertEquals(another.value, cell.value)
        self.assertEquals(another.borders, cell.borders)
        self.assertEquals(another.color, cell.color)
        self.assertEquals(another.font, cell.font)
        self.assertEquals(another.fontstyle, cell.fontstyle)

    def test_empty_font(self):
        key = get_random_cell_key()
        value = random.choice(string.ascii_letters)
        cell = Cell(key, value, font="")
        another = Cell.from_primitive(cell.to_primitive())
        self.assertEquals(another.key, cell.key)
        self.assertEquals(another.value, cell.value)
        self.assertEquals(another.borders, cell.borders)
        self.assertEquals(another.color, cell.color)
        self.assertEquals(another.font, cell.font)
        self.assertEquals(another.fontstyle, cell.fontstyle)
