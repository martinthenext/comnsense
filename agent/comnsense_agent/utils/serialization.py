import logging
import copy
import functools
from collections import Sequence, Mapping, Set

import json
import msgpack

logger = logging.getLogger(__name__)


def get_content(obj):
    if hasattr(obj, "__getstate__"):
        return get_content(obj.__getstate__())
    elif hasattr(obj, "__slots__"):
        content = {}
        for key in obj.__slots__:
            key = key.lstrip("_")
            content[key] = get_content(getattr(obj, key))
        return content
    elif isinstance(obj, (str, unicode)):
        return obj
    elif isinstance(obj, Mapping):  # like dict
        content = {}
        for key, value in obj.items():
            if key.startswith("_"):
                continue
            content[key] = get_content(value)
        return content
    elif isinstance(obj, (Sequence, Set)):  # like list or set
        return [get_content(x) for x in obj]
    elif hasattr(obj, "__dict__"):
        return get_content(obj.__dict__)
    else:
        return obj  # primitive type


def restore_content(obj, content):
    dct = {}
    if hasattr(obj, "__setstate__"):
        obj.__setstate__(content)
        return obj
    for key, value in content.iteritems():
        setattr(obj, key, copy.deepcopy(value))
    return obj


def Serializable(provider):
    PROVIDERS = {
        "json":    (json.dumps,
                    json.loads),
        "msgpack": (functools.partial(msgpack.packb, use_bin_type=True),
                    functools.partial(msgpack.unpackb, encoding='utf-8'))
    }

    assert provider in PROVIDERS

    def serialize(self):
        content = get_content(self)
        return PROVIDERS[provider][0](content)

    @classmethod
    def deserialize(cls, data):
        obj = cls.__new__(cls)
        content = PROVIDERS[provider][1](data)
        return restore_content(obj, content)

    return type(provider.title() + "Serializable", (object,),
                {"serialize": serialize, "deserialize": deserialize})


JsonSerializable = Serializable("json")
MsgpackSerializable = Serializable("msgpack")
