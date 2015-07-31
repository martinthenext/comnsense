import pytest
import allure
from hamcrest import *

from ..fixtures.classes import NewStyleClass

from comnsense_agent.multiplexer.multiplexer import Multiplexer


@allure.feature("Multiplexer")
def test_multiplexer_abstract_method():
    klass, obj = NewStyleClass({}, Multiplexer)
    with pytest.raises(NotImplementedError):
        obj.merge("event", "actions")
