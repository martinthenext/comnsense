import pytest
import allure
import mock
from hamcrest import *

from comnsense_agent.message import Message
from comnsense_agent.data import Signal

from .fixtures.network import port, host
from .fixtures.excel import workbook


@pytest.fixture(scope="module")
def fe_connection(host, port):
    return "tcp://%s:%d" % (host, port)


@pytest.fixture(scope="module")
def be_connection(host, port):
    return "tcp://%s:%d" % (host, port + 1)


@pytest.fixture(scope="module")
def server_address():
    return "http://comnsense.io"


@pytest.yield_fixture(autouse=True)
def dummy_router(monkeypatch, be_connection):

    from comnsense_agent.socket.zmq_socket import ZMQRouter

    def new(cls, *args, **kwargs):
        router = mock.Mock()
        router.bind_unused_port.return_value = be_connection
        return router

    monkeypatch.setattr(ZMQRouter, "__new__", classmethod(new))
    monkeypatch.setattr(ZMQRouter, "__init__", lambda *x, **y: None)

    yield None

    monkeypatch.undo()
    monkeypatch.undo()


@pytest.yield_fixture(autouse=True)
def dummy_client(monkeypatch):
    client = mock.Mock()

    from comnsense_agent.serverstream import ServerStream

    def new(cls, *args, **kwargs):
        return client

    monkeypatch.setattr(ServerStream, "__new__", classmethod(new))
    monkeypatch.setattr(ServerStream, "__init__", lambda *x, **y: None)

    yield None

    monkeypatch.undo()
    monkeypatch.undo()


@pytest.yield_fixture(autouse=True)
def dummy_worker(monkeypatch):
    monkeypatch.setattr(
        "comnsense_agent.worker.create_new_worker",
        lambda ident, bind: mock.Mock())
    yield None
    monkeypatch.undo()


@pytest.fixture(scope="module")
def loop():
    return mock.Mock()


@pytest.fixture
def event_msg(workbook):
    return Message.event("event", workbook)


@pytest.fixture
def action_msg(workbook):
    return Message.action("action", workbook)


@pytest.fixture
def request_msg(workbook):
    return Message.request("request", workbook)


@pytest.fixture
def response_msg(workbook):
    return Message.response("response", workbook)


@pytest.fixture
def signal_msg(workbook):
    return Message.signal(Signal.ready(), workbook)


@pytest.fixture
def message(workbook, request):
    return globals()[request.param + "_msg"](workbook)


@pytest.fixture()
def agent(fe_connection, server_address, loop):
    import comnsense_agent.agent
    return comnsense_agent.agent.Agent(fe_connection, server_address, loop)


@allure.feature("Agent")
def test_agent_create_frontend_socket(agent, fe_connection, loop):
    assert_that(agent.frontend.bind.mock_calls,
                equal_to([mock.call(fe_connection, loop)]))
    assert_that(agent.frontend.on_recv.mock_calls,
                equal_to([mock.call(agent.frontend_routine)]))


@allure.feature("Agent")
def test_agent_create_backend_socket(agent, be_connection, loop):
    assert_that(agent.backend.bind_unused_port.mock_calls,
                equal_to([mock.call(loop)]))
    assert_that(agent.backend_bind, equal_to(be_connection))
    assert_that(agent.backend.on_recv.mock_calls,
                equal_to([mock.call(agent.backend_routine)]))


@allure.feature("Agent")
def test_agent_create_client_socket(agent, server_address, loop):
    assert_that(agent.client.on_recv.mock_calls,
                equal_to([mock.call(agent.client_routine)]))


@allure.feature("Agent")
@pytest.mark.parametrize("message", ["event", "action", "request", "signal"],
                         indirect=True)
def test_client_routine_nothing(agent, message):
    agent.client_routine(message)
    assert_that(agent.frontend.send.mock_calls, equal_to([]))
    assert_that(agent.backend.send.mock_calls, equal_to([]))
    assert_that(agent.client.send.mock_calls, equal_to([]))


@allure.feature("Agent")
def test_client_routine_response(agent, response_msg):
    agent.client_routine(response_msg)
    assert_that(agent.frontend.send.mock_calls, equal_to([]))
    assert_that(agent.backend.send.mock_calls,
                equal_to([mock.call(response_msg)]))
    assert_that(agent.client.send.mock_calls, equal_to([]))


@allure.feature("Agent")
@pytest.mark.parametrize("message",
                         ["response", "action", "request", "signal"],
                         indirect=True)
def test_frontend_routine_nothing(agent, message):
    agent.frontend_routine(message)
    assert_that(agent.frontend.send.mock_calls, equal_to([]))
    assert_that(agent.backend.send.mock_calls, equal_to([]))
    assert_that(agent.client.send.mock_calls, equal_to([]))


@allure.feature("Agent")
def test_frontend_routine_new_worker(agent, event_msg):
    agent.frontend_routine(event_msg)
    assert_that(agent.workers, has_key(event_msg.ident))
    assert_that(agent.frontend.send.mock_calls, equal_to([]))
    assert_that(agent.backend.send.mock_calls,
                equal_to([mock.call(event_msg)]))
    assert_that(agent.client.send.mock_calls, equal_to([]))


@allure.feature("Agent")
def test_frontend_routine_event_to_alive_worker(agent, event_msg):
    worker = mock.Mock()
    worker.is_alive.return_value = True
    agent.workers[event_msg.ident] = worker

    agent.frontend_routine(event_msg)
    assert_that(agent.workers, equal_to({event_msg.ident: worker}))
    assert_that(agent.frontend.send.mock_calls, equal_to([]))
    assert_that(agent.backend.send.mock_calls,
                equal_to([mock.call(event_msg)]))
    assert_that(agent.client.send.mock_calls, equal_to([]))


@allure.feature("Agent")
def test_frontend_routine_event_to_alive_worker(agent, event_msg):
    worker = mock.Mock()
    worker.is_alive.return_value = False
    agent.workers[event_msg.ident] = worker

    agent.frontend_routine(event_msg)
    assert_that(agent.workers.keys(), equal_to([event_msg.ident]))
    assert_that(agent.workers[event_msg.ident], is_not(equal_to(worker)))
    assert_that(agent.frontend.send.mock_calls, equal_to([]))
    assert_that(agent.backend.send.mock_calls,
                equal_to([mock.call(event_msg)]))
    assert_that(agent.client.send.mock_calls, equal_to([]))


@allure.feature("Agent")
def test_backend_routine_action(agent, action_msg):
    agent.backend_routine(action_msg)
    assert_that(agent.frontend.send.mock_calls,
                equal_to([mock.call(action_msg)]))
    assert_that(agent.backend.send.mock_calls, equal_to([]))
    assert_that(agent.client.send.mock_calls, equal_to([]))


@allure.feature("Agent")
def test_backend_routine_request(agent, request_msg):
    agent.backend_routine(request_msg)
    assert_that(agent.frontend.send.mock_calls, equal_to([]))
    assert_that(agent.backend.send.mock_calls, equal_to([]))
    assert_that(agent.client.send.mock_calls,
                equal_to([mock.call(request_msg)]))
