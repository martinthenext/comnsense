import pytest
import allure
import zmq
from zmq.eventloop import ioloop, zmqstream

from comnsense_agent.message import Message
from comnsense_agent.data import Action


@pytest.yield_fixture()
def addin(scenario, agent_host, agent_port):
    class AddIn(object):
        def __init__(self, host, port, scenario):
            self.connection = "tcp://%s:%d" % (host, port)
            self.scenario = scenario

        def setup_socket(self, loop, ctx):
            socket = ctx.socket(zmq.DEALER)
            socket.setsockopt(zmq.IDENTITY, self.scenario.workbook.identity)
            socket.connect(self.connection)
            return zmqstream.ZMQStream(socket, loop)

        def run(self, loop, interval=500, initial_interval=3000):
            ctx = zmq.Context()
            stream = self.setup_socket(loop, ctx)
            iterator = self.scenario.__iter__()

            def on_recv(msg):
                if not msg.is_action():
                    return

                action = Action.deserialize(msg.payload)
                answer = self.scenario.apply(action)
                if answer:
                    stream.send_multipart(list(Message.event(answer)))

            def send():
                event = next(iterator)
                stream.send_multipart(list(Message.event(event)))

            def stop():
                loop.stop()

            stream.on_recv(Message.call(on_recv))

            for i in xrange(len(self.scenario.steps)):
                callback = ioloop.DelayedCallback(
                    send, i if i == 0 else initial_interval + interval * i,
                    io_loop=loop)
                callback.start()

            callback = ioloop.DelayedCallback(
                stop, initial_interval + interval * len(self.scenario.steps),
                io_loop=loop)
            callback.start()

            loop.start()
            stream.close(1)
            ctx.destroy()
            ctx.term()

    addin = AddIn(agent_host, agent_port, scenario)
    with allure.step("start addin: %s" % addin.connection):
        for sheet in addin.scenario.workbook.sheets():
            allure.attach("workbook.%s" % sheet,
                          addin.scenario.workbook.serialize(sheet))
    yield addin
