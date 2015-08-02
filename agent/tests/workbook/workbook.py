import allure
import pytest
import string
import re
import copy


from comnsense_agent.data import Cell


class Workbook(object):
    DEFAULT_SHEET_NAME = "Sheet 1"
    SHEET_NAME_SYMBOL = "="
    HEADER_SYMBOL = "-"
    COLUMN_SYMBOL = "|"
    START_ROW = 1
    TAG_PATTERN = re.compile(r':(\w+)::(\w+)', re.U | re.S)

    def __init__(self, identity, sheet=None):
        self.identity = identity
        if sheet is None:
            self._sheets = {self.DEFAULT_SHEET_NAME: []}
        else:
            self._sheets = self._parse_sheet(sheet)

    def _parse_sheet(self, sheet):
        cells = []
        lines = self._get_lines(sheet)
        sheetname = self._get_sheet_name(lines)
        columns = self._get_columns(lines)
        for number, line in enumerate(lines, self.START_ROW):
            row = []
            values = self._get_values(line)
            for column, value in zip(columns, values):
                key = "$%s$%d" % (column, number)
                value, tags = self._extract_tags(value)
                cell = Cell(key, value)
                self._apply_tags(cell, tags)
                row.append(cell)
            cells.append(row)
        return {sheetname: cells}

    def _get_lines(self, sheet):
        lines = (x.strip() for x in sheet.splitlines())
        return [x for x in lines if x]

    def _get_sheet_name(self, lines):
        if len(lines) < 2:
            return self.DEFAULT_SHEET_NAME
        length = max(map(len, lines))
        if lines[-2] == self.SHEET_NAME_SYMBOL * length:
            name = lines[-1]
            del lines[-1]
            del lines[-1]
            return name
        else:
            return self.DEFAULT_SHEET_NAME

    def _get_columns_count(self, lines):
        counts = [len(x.split(self.COLUMN_SYMBOL)) for x in lines]
        if len(set(counts)) != 1:
            raise RuntimeError("Different count of columns in rows")
        return counts[0]

    def _get_columns(self, lines):
        if len(lines) < 2:
            col_count = self._get_columns_count(lines)
            return string.ascii_uppercase[:col_count]
        length = max(map(len, lines))
        if lines[1] == self.HEADER_SYMBOL * length:
            columns = self._get_values(lines[0])
            del lines[0]
            del lines[0]
            return columns
        else:
            col_count = self._get_columns_count(lines)
            return string.ascii_uppercase[:col_count]

    def _get_values(self, line):
        return [x.strip() for x in line.split(self.COLUMN_SYMBOL)]

    def _extract_tags(self, value):
        match = self.TAG_PATTERN.search(value)
        if match:
            value = value[:match.start()] + value[match.end():]
            tags = {match.group(1): match.group(2)}
            value, new_tags = self._extract_tags(value)
            tags.update(new_tags)
            return value, tags
        else:
            return value, {}

    def _apply_tags(self, cell, tags):
        for key, value in tags.items():
            if key == "color":
                cell.color = int(value)
            else:
                raise NotImplementedError("tag %s not yet implemented" % key)

    def _get_cell_value(self, cell):
        value = cell.value
        if cell.color is not None:
            value += ":color::%d" % cell.color
        return value

    def sheets(self):
        return self._sheets.keys()

    def columns(self, sheet):
        cells = self._sheets[sheet]
        if not cells:
            return []
        columns = []
        for cell in cells[0]:
            columns.append(cell.column)
        return columns

    def serialize(self, sheetname):
        cells = self._sheets[sheetname]
        col_values = [[x] for x in self.columns(sheetname)]
        for row in cells:
            for i, cell in enumerate(row):
                value = self._get_cell_value(cell)
                col_values[i].append(value)
        for i, values in enumerate(col_values[:]):
            length = max(map(len, values))
            col_values[i] = map(lambda x: x + " " * (length - len(x)), values)
        result = []
        for line in zip(*col_values):
            result.append(self.COLUMN_SYMBOL.join(line))
        result.append(sheetname)
        length = max(map(len, result))
        result.insert(1, self.HEADER_SYMBOL * length)
        result.insert(-1, self.SHEET_NAME_SYMBOL * length)
        return "\n".join(result)

    def get(self, sheetname, key):
        cells = self._sheets[sheetname]
        for row in cells:
            for cell in row:
                if cell.key == key:
                    return copy.deepcopy(cell)

    def put(self, sheetname, cell):
        cells = self._sheets[sheetname]
        columns = self.columns(sheetname)
        while int(cell.row) > len(cells):
            cells.append(
                [Cell("$%s$%d" % (x, len(cells) + 1), "") for x in columns])
        if cell.column in columns:
            col = columns.index(cell.column)
            cells[int(cell.row) - 1][col] = copy.deepcopy(cell)
        else:
            # append column
            for i, row in enumerate(cells[:]):
                if i + 1 == int(cell.row):
                    cells[i].append(copy.deepcopy(cell))
                else:
                    cells[i].append(Cell("$%s$%d" % (cell.column, i + 1), ""))

    def __eq__(self, another):
        if not isinstance(another, self.__class__):
            return False
        return self.identity == another.identity and \
            self._sheets == another._sheets

    def __ne__(self, another):
        return not self.__eq__(another)
