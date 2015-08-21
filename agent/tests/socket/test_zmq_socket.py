import pytest
import allure
import random
import threading
import multiprocessing
import time
import logging
from hamcrest import *

import zmq
from zmq.eventloop import ioloop, zmqstream

from ..fixtures.async import zmq_io_loop as io_loop
from ..fixtures.excel import workbook
from ..fixtures.network import host, port
from comnsense_agent.message import Message
from comnsense_agent.data import Event
from comnsense_agent.data import Signal

from comnsense_agent.socket import ZMQRouter, ZMQDealer


@pytest.yield_fixture(params=[
    Event.Type.WorkbookOpen,
    Event.Type.WorkbookBeforeClose])
def message(workbook, request):
    event = Event(request.param, workbook)
    yield Message.event(event)


@pytest.yield_fixture(params=["simple", "dealer"])
def client(request):
    stop = Message.signal(Signal.stop())

    def simple(message, connection, loop, count):
        messages = []
        ctx = zmq.Context()
        socket = ctx.socket(zmq.DEALER)
        socket.connect(connection)
        stream = zmqstream.ZMQStream(socket, loop)

        def check(data):
            messages.append(data)
            answer = Message(*data)
            if len(messages) < count:
                assert_that(answer.kind, equal_to(message.kind))
                assert_that(answer.payload, equal_to(message.payload))
                stream.send_multipart(list(message))
            elif len(messages) == count:
                assert_that(answer.kind, equal_to(message.kind))
                assert_that(answer.payload, equal_to(message.payload))
                stream.send_multipart(list(stop))
            else:
                assert_that(answer.kind, equal_to(stop.kind))
                stream.close(1000)
                loop.stop()

        stream.on_recv(check)
        stream.send_multipart(list(message))
        return messages

    def dealer(message, connection, loop, count):
        messages = []
        socket = ZMQDealer()
        socket.connect(connection, loop)

        def check(msg):
            messages.append(msg)
            if len(messages) < count:
                assert_that(msg.kind, equal_to(message.kind))
                assert_that(msg.payload, equal_to(message.payload))
                socket.send(message)
            elif len(messages) == count:
                assert_that(msg.kind, equal_to(message.kind))
                assert_that(msg.payload, equal_to(message.payload))
                socket.send(stop)
            else:
                assert_that(msg.kind, equal_to(stop.kind))
                socket.close()
                loop.stop()

        socket.on_recv(check)
        socket.send(message)
        return messages

    if request.param == "simple":
        yield simple
    elif request.param == "dealer":
        yield dealer


@pytest.yield_fixture(params=[True, False], ids=["regular", "random"])
def connection(host, port, request):
    if not request.param:
        yield None
    else:
        yield "tcp://%s:%s" % (host, port)


@allure.feature("Socket")
@allure.story("ZMQ Echo Server on ZMQRouter")
@pytest.mark.timeout(1)
def test_zmq_socket_echo(io_loop, connection, message, client):

    def server(connection, loop):
        socket = ZMQRouter()
        if connection is None:
            address = socket.bind_unused_port(loop)
        else:
            socket.bind(connection, loop)
            address = connection

        def on_recv(msg):
            socket.send(msg)

        def on_send(msg):
            if msg.is_signal():
                socket.close()

        socket.on_recv(on_recv)
        socket.on_send(on_send)
        return address

    address = server(connection, io_loop)
    count = 10
    messages = client(message, address, io_loop, count)
    assert_that(messages, has_length(0))
    io_loop.start()
    assert_that(messages, has_length(count + 1))
