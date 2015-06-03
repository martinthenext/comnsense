# coding=utf-8
import pytest
import unittest
import random
import string


from comnsense_agent.data import Signal, SignalError


class TestSignal(unittest.TestCase):
    def test_serialize_int(self):
        one = Signal(random.choice(Signal.Code.__members__.values()),
                     random.choice(range(10)))
        data = one.serialize()
        another = Signal.deserialize(data)
        self.assertEquals(one, another)

    def test_serialize_int(self):
        one = Signal(random.choice(Signal.Code.__members__.values()),
                     random.sample(string.ascii_letters, 10))
        data = one.serialize()
        another = Signal.deserialize(data)
        self.assertEquals(one, another)

    def test_serialize_none(self):
        one = Signal(random.choice(Signal.Code.__members__.values()))
        data = one.serialize()
        another = Signal.deserialize(data)
        self.assertEquals(one, another)

    def test_serialize_unicode(self):
        one = Signal(random.choice(Signal.Code.__members__.values()),
                     u'траливали')
        data = one.serialize()
        another = Signal.deserialize(data)
        self.assertEquals(one, another)
