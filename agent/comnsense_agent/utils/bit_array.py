import binascii
import logging

import bitarray

logger = logging.getLogger(__name__)


class BitArray(object):
    __slots__ = ('__array__',)

    def __init__(self, length=0):
        self.__array__ = bitarray.bitarray()
        self.advance(length)

    def advance(self, length):
        if length > len(self.__array__):
            self.__array__.extend([False] * (length - len(self.__array__)))
            self.__array__.fill()

    def __getitem__(self, index):
        if index >= len(self.__array__):
            return False
        return self.__array__[index]

    def __setitem__(self, index, value):
        self.advance(index + 1)
        self.__array__[index] = bool(value)

    def __len__(self):
        return len(self.__array__)

    def __getstate__(self):
        return binascii.b2a_base64(self.__array__.tobytes())

    def __setstate__(self, data):
        self.__array__.frombytes(binascii.a2b_base64(data))

    def __eq__(self, other):
        return self.__array__ == other.__array__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return repr(self.__array__.tobytes())
