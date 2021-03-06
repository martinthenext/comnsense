import enum
import logging

from types import NoneType

logger = logging.getLogger(__name__)


class Border(object):
    __slots__ = ("_weight", "_linestyle")

    @enum.unique
    class Weight(enum.IntEnum):
        xlMedium = -4138
        xlHairline = 1
        xlThin = 2
        xlThick = 4

    @enum.unique
    class LineStyle(enum.IntEnum):
        xlLineStyleNone = -4142
        xlDouble = -4119
        xlDot = -4118
        xlDash = -4115
        xlContinuous = 1
        xlDashDot = 4
        xlDashDotDot = 5
        xlSlantDashDot = 13

    def __init__(self, weight, linestyle):
        self.weight = weight
        self.linestyle = linestyle

    @property
    def weight(self):
        return self._weight.value

    @weight.setter
    def weight(self, value):
        assert isinstance(value, (int, Border.Weight))
        if isinstance(value, int):
            value = Border.Weight(value)
        self._weight = value

    @property
    def linestyle(self):
        return self._linestyle.value

    @linestyle.setter
    def linestyle(self, value):
        assert isinstance(value, (int, Border.LineStyle))
        if isinstance(value, int):
            value = Border.LineStyle(value)
        self._linestyle = value

    def to_primitive(self):
        return [self.weight, self.linestyle]

    @staticmethod
    def from_primitive(obj):
        return Border(*obj)

    def __repr__(self):
        return "Border: %s" % self.to_primitive()

    def __eq__(self, another):
        return self.weight == another.weight and \
                self.linestyle == another.linestyle

    def __ne__(self, another):
        return not self.__eq__(another)


class Borders(object):
    __slots__ = ("top", "left", "bottom", "right")

    def __init__(self, top=None, left=None, bottom=None, right=None):
        assert isinstance(top, (Border, NoneType))
        assert isinstance(left, (Border, NoneType))
        assert isinstance(bottom, (Border, NoneType))
        assert isinstance(right, (Border, NoneType))
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right

    def to_primitive(self):
        obj = {}
        if self.top:
            obj["top"] = self.top.to_primitive()
        if self.left:
            obj["left"] = self.left.to_primitive()
        if self.bottom:
            obj["bottom"] = self.bottom.to_primitive()
        if self.right:
            obj["right"] = self.right.to_primitive()
        if not obj:
            return None
        return obj

    @staticmethod
    def from_primitive(obj):
        if obj is None:
            return Borders()
        items = obj.items()
        items = [(x[0], Border.from_primitive(x[1])) for x in items
                 if x[1] is not None]
        kwargs = dict(items)
        return Borders(**kwargs)

    def __repr__(self):
        return "Borders: %s" % self.to_primitive()

    def __eq__(self, another):
        for attr in Borders.__slots__:
            if getattr(self, attr) != getattr(another, attr):
                return False
        return True

    def __ne__(self, another):
        return not self.__eq__(another)


class Cell(object):
    __slots__ = ("key", "value", "font", "color", "fontstyle", "borders")

    @enum.unique
    class FontStyle(enum.IntEnum):
        bold = 1
        italic = 2
        underline = 4

    def __init__(self, key, value,
                 font=None, color=None,
                 fontstyle=None, borders=None):
        self.key = key
        self.value = value
        if borders is None:
            borders = Borders()
        self.borders = borders
        self.color = color
        self.font = font
        self.fontstyle = fontstyle

        assert key is not None
        assert isinstance(color, (int, NoneType))
        assert isinstance(fontstyle, (int, NoneType))
        assert isinstance(borders, Borders)
        assert isinstance(font, (unicode, str, NoneType))

    def _check_fontstyle(self, mask):
        assert isinstance(mask, int)
        if self.fontstyle is None:
            return False
        return (self.fontstyle & mask) != 0

    def _set_fontstyle(self, mask, value):
        assert isinstance(mask, int)
        if self.fontstyle is None:
            self.fontstyle = 0
        if value:
            self.fontstyle |= mask
        else:
            self.fontstyle &= ~mask

    @property
    def bold(self):
        return self._check_fontstyle(Cell.FontStyle.bold.value)

    @bold.setter
    def bold(self, value):
        self._set_fontstyle(Cell.FontStyle.bold.value, value)

    @property
    def italic(self):
        return self._check_fontstyle(Cell.FontStyle.italic.value)

    @italic.setter
    def italic(self, value):
        self._set_fontstyle(Cell.FontStyle.italic.value, value)

    @property
    def underline(self):
        return self._check_fontstyle(Cell.FontStyle.underline.value)

    @underline.setter
    def underline(self, value):
        self._set_fontstyle(Cell.FontStyle.underline.value, value)

    @property
    def column(self):
        return self.key.split("$")[1]

    @property
    def row(self):
        return self.key.split("$")[2]

    def to_primitive(self):
        obj = {"key": self.key}
        if self.value is not None:
            obj["value"] = self.value
        borders = self.borders.to_primitive()
        if borders:
            obj["borders"] = borders
        if self.color is not None:
            obj["color"] = self.color
        if self.font is not None:
            obj["font"] = self.font
        if self.fontstyle is not None:
            obj["fontstyle"] = self.fontstyle
        return obj

    @staticmethod
    def from_primitive(obj):
        key = obj.get("key")
        value = obj.get("value")
        kwargs = {}
        if obj.get("borders"):
            borders = Borders.from_primitive(obj.get("borders"))
            kwargs["borders"] = borders
        kwargs["color"] = obj.get("color")
        kwargs["font"] = obj.get("font")
        kwargs["fontstyle"] = obj.get("fontstyle")
        return Cell(key, value, **kwargs)

    @staticmethod
    def table_to_primitive(table):
        return [[cell.to_primitive() for cell in row] for row in table]

    @staticmethod
    def table_from_primitive(obj):
        return [[Cell.from_primitive(data) for data in row] for row in obj]

    def __repr__(self):
        main = "{%s: %s}" % (self.key, self.value)
        attrs = self.to_primitive()
        del attrs["key"]
        if self.value is not None:
            del attrs["value"]
        items = attrs.items()
        items = ["%s=%s" % x for x in items]
        if items:
            main = "%s[%s]" % (main, ", ".join(items))
        return main.encode('utf-8')

    def __eq__(self, another):
        for attr in Cell.__slots__:
            if getattr(self, attr) != getattr(another, attr):
                return False
        return True

    def __ne__(self, another):
        return not self.__eq__(another)
