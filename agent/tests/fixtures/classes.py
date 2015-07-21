import pytest
import random
import copy

from ..common import get_random_string


def OldStyleClass(dct, parent=None):
    if parent is not None:
        class OldStyle(parent):
            pass
    else:
        class OldStyle:
            pass

    obj = OldStyle()
    obj.__dict__ = dct
    return OldStyle, obj


def NewStyleClass(dct, parent=None):
    if parent is None:
        parent = object

    klass = type("NewStyle", (parent,),
                 {"__eq__": lambda s, o: s.__dict__ == o.__dict__})
    obj = klass()
    obj.__dict__ = dct
    return klass, obj


def SlotsClass(dct, parent=None):
    if parent is None:
        parent = object

    def eq(self, other):
        return [getattr(self, x) for x in self.__slots__] == \
                [getattr(other, x) for x in other.__slots__]

    klass = type("Slots", (parent,), {"__slots__": dct.keys(), "__eq__": eq})
    obj = klass()
    for key, value in dct.items():
        setattr(obj, key, value)
    return klass, obj


def PrivateSlotsClass(dct, parent=None):
    if parent is None:
        parent = object

    def getter(key):
        return (lambda o: getattr(o, "_%s" % key))

    def setter(key):
        return (lambda o, v: setattr(o, "_%s" % key, v))

    def eq(self, other):
        return [getattr(self, x) for x in self.__slots__] == \
                [getattr(other, x) for x in other.__slots__]

    slots = {"__slots__": map(lambda x: "_%s" % x, dct.keys()), "__eq__": eq}
    props = {x: property(getter(x), setter(x)) for x in dct.keys()}
    attrs = {}
    attrs.update(slots)
    attrs.update(props)

    klass = type("PrivateSlots", (parent,), attrs)
    obj = klass()
    for key, value in dct.items():
        setattr(obj, "_%s" % key, copy.deepcopy(value))
    return klass, obj


def StateClass(dct, parent=None):
    def getstate(self):
        return self.my

    def setstate(self, state):
        self.my = state

    if parent is None:
        parent = object

    klass = type("State", (parent,),
                 {"__getstate__": getstate,
                  "__setstate__": setstate,
                  "__eq__": lambda s, o: s.my == o.my})
    obj = klass()
    obj.my = dct
    return klass, obj


CLASSES = [OldStyleClass,
           NewStyleClass,
           SlotsClass,
           StateClass,
           PrivateSlotsClass]


def RandomClass(dct, parent=None):
    return random.choice(CLASSES)(dct, parent)


@pytest.yield_fixture
def simple_class_fields():
    base = {"a": random.randint(0, 10),
            "b": get_random_string(),
            "c": random.choice([True, False]),
            "d": None,
            "e": [get_random_string()],
            "f": {"a": get_random_string()}}
    yield base


@pytest.yield_fixture
def complex_class_fields():
    base = next(simple_class_fields())
    attrs = copy.deepcopy(base)
    attrs['g'] = RandomClass(base)[1]
    attrs['h'] = [RandomClass(base)[1]]
    attrs['j'] = {'a': RandomClass(base)[1]}
    dct = copy.deepcopy(base)
    dct['g'] = base
    dct['h'] = [base]
    dct['j'] = {'a': base}
    yield attrs, dct
