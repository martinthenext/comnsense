import logging
import enum

from types import NoneType

logger = logging.getLogger(__name__)


class Border(object):
    __slots__ = ("_weight", "_linestyle")

    @enum.unique
    class LineStyle(enum.IntEnum):
        xlMedium = -4138
        xlHairline = 1
        xlThin = 2
        xlThick = 4

    @enum.unique
    class Weight(enum.IntEnum):
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

    def to_python_object(self):
        return [self.weight, self.linestyle]

    @staticmethod
    def from_python_object(obj):
        return Border(*obj)

    def __repr__(self):
        return "Border: %s" % self.to_python_object()

    def __eq__(self, another):
        return self._weight == another._weight and \
                self._linestyle == another._linestyle

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

    def to_python_object(self):
        obj = {}
        if self.top:
            obj["top"] = self.top.to_python_object()
        if self.left:
            obj["left"] = self.left.to_python_object()
        if self.bottom:
            obj["bottom"] = self.bottom.to_python_object()
        if self.right:
            obj["right"] = self.right.to_python_object()
        if not obj:
            return None
        return obj

    @staticmethod
    def from_python_object(obj):
        if obj is None:
            return Borders()
        items = obj.items()
        items = [(x[0], Border.from_python_object(x[1])) for x in items
                 if x[1] is not None]
        kwargs = dict(items)
        return Borders(**kwargs)

    def __repr__(self):
        return "Borders: %s" % self.to_python_object()

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
        assert isinstance(font, (str, NoneType))

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

    def to_python_object(self):
        obj = {"key": self.key, "value": self.value}
        borders = self.borders.to_python_object()
        if borders:
            obj["borders"] = borders
        if self.color:
            obj["color"] = self.color
        if self.font:
            obj["font"] = self.font
        if self.fontstyle:
            obj["fontstyle"] = self.fontstyle
        return obj

    @staticmethod
    def from_python_object(obj):
        key = obj.get("key")
        value = obj.get("value")
        kwargs = {}
        if obj.get("borders"):
            borders = Borders.from_python_object(obj.get("borders"))
            kwargs["borders"] = borders
        kwargs["color"] = obj.get("color")
        kwargs["font"] = obj.get("font")
        kwargs["fontstyle"] = obj.get("fontstyle")
        return Cell(key, value, **kwargs)

    def __repr__(self):
        main = "{%s: %s}" % (self.key, self.value)
        attrs = self.to_python_object()
        del attrs["key"]
        del attrs["value"]
        items = attrs.items()
        items = ["%s=%s" % x for x in items]
        if items:
            return "%s[%s]" % (main, ", ".join(items))
        return main

    def __eq__(self, another):
        for attr in Cell.__slots__:
            if getattr(self, attr) != getattr(another, attr):
                raise Exception(attr)
                return False
        return True

    def __ne__(self, another):
        return not self.__eq__(another)
