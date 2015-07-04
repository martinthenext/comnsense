import unittest
import pytest
import random
import string


from comnsense_agent.data import Border
from comnsense_agent.data import Borders
from comnsense_agent.data import Cell


def get_random_linestyle():
    styles = Border.LineStyle.__members__.values()
    return random.choice(styles)


def get_random_weight():
    weights = Border.Weight.__members__.values()
    return random.choice(weights)


def get_random_border():
    linestyle = get_random_linestyle()
    weight = get_random_weight()
    return Border(weight, linestyle)


def get_random_border_side():
    sides = {"top", "left", "bottom", "right"}
    side = random.choice(list(sides))
    other = sides - {side}
    return side, other


def get_random_borders():
    side, _ = get_random_border_side()
    border = get_random_border()
    return Borders.from_python_object({side: border.to_python_object()})


def get_random_cell_key():
    return "$%s$%d" % (
        random.choice(string.ascii_uppercase),
        random.choice(range(1, 65535)))


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
            border.to_python_object(),
            [weight.value, linestyle.value])

    def test_deserialization(self):
        linestyle = get_random_linestyle()
        weight = get_random_weight()
        obj = [weight.value, linestyle.value]
        border = Border.from_python_object(obj)
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
        self.assertEquals(borders.to_python_object(), None)

    def test_trivial_deserialization(self):
        borders = Borders.from_python_object(None)
        self.assertEquals(borders.top, None)
        self.assertEquals(borders.left, None)
        self.assertEquals(borders.bottom, None)
        self.assertEquals(borders.right, None)

    def test_single(self):
        side, other = get_random_border_side()
        border = get_random_border()
        original = {side: border.to_python_object()}
        borders = Borders.from_python_object(original)
        self.assertEquals(getattr(borders, side), border)
        for one in other:
            self.assertEquals(getattr(borders, one), None)
        self.assertEquals(borders.to_python_object(), original)


class TestCell(unittest.TestCase):
    def test_trivial(self):
        key = get_random_cell_key()
        value = random.choice(string.ascii_letters)
        original = {"key": key, "value": value}
        cell = Cell(key, value)
        self.assertEquals(key, cell.key)
        self.assertEquals(value, cell.value)
        obj = cell.to_python_object()
        self.assertEquals(obj, original)
        another = Cell.from_python_object(original)
        self.assertEquals(cell, another)

    def test_borders(self):
        key = get_random_cell_key()
        value = random.choice(string.ascii_letters)
        borders = get_random_borders()
        original = {
            "key": key,
            "value": value,
            "borders": borders.to_python_object()
        }
        cell = Cell(key, value, borders=borders)
        self.assertEquals(key, cell.key)
        self.assertEquals(value, cell.value)
        self.assertEquals(borders, cell.borders)
        obj = cell.to_python_object()
        self.assertEquals(obj, original)
        another = Cell.from_python_object(original)
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
            "borders": borders.to_python_object(),
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
        obj = cell.to_python_object()
        self.assertEquals(obj, original)
        another = Cell.from_python_object(original)
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
