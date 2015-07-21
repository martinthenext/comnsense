# coding=utf-8
import random
import string
import uuid

from comnsense_agent.data import Border
from comnsense_agent.data import Borders
from comnsense_agent.data import Cell


RUSSIAN_LETTERS = u"абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
TEST_LETTERS = string.ascii_letters + RUSSIAN_LETTERS + RUSSIAN_LETTERS.upper()

COMNSENSE_WIKI = 'https://github.com/martinthenext/comnsense/wiki'


def get_random_workbook_id():
    return str(uuid.uuid1())


def get_random_string():
    return u"".join(random.sample(TEST_LETTERS, 10))


def get_random_sheet_name():
    return get_random_string()


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
    return Borders.from_primitive({side: border.to_primitive()})


def get_random_cell_key():
    return "$%s$%d" % (
        random.choice(string.ascii_uppercase),
        random.choice(range(1, 65535)))


def get_random_cell_value():
    return u"".join(random.sample(TEST_LETTERS, 100))


def get_random_cell_int_value():
    return str(random.choice(range(1, 65535)))


def get_random_cell(key=None, value=None):
    if key is None:
        key = get_random_cell_key()
    if value is None:
        value = get_random_cell_value()
    cell = Cell(key, value)
    if random.randint(0, 1) > 0:
        cell.borders = get_random_borders()
    if random.randint(0, 1) > 0:
        cell.font = u"".join(random.sample(TEST_LETTERS, 10))
    if random.randint(0, 1) > 0:
        cell.fontstyle = random.randint(0, 7)
    if random.randint(0, 1) > 0:
        cell.color = random.randint(0, 10)
    return cell


def get_random_table(cols, rows):
    result = []
    for index in range(1, rows + 2):
        row = []
        for letter in string.ascii_uppercase[:cols + 1]:
            row.append(get_random_cell("$%s$%d" % (letter, index)))
        result.append(row)
    return result
