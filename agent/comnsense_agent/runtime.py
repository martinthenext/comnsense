import logging
import uuid

from comnsense_agent.message import Message
from comnsense_agent.data import Event, Action, Request, Signal, Response
from comnsense_agent.data import Cell, Border
from comnsense_agent.context import Context

logger = logging.getLogger(__name__)


class State:
    pass


class WaitingWorkbookID:
    """
    Waiting for workbook id from excel
    """
    def next(self, context, msg):
        if msg.is_event():
            event = Event.deserialize(msg.payload)
            context.workbook = event.workbook
        elif msg.is_signal():
            signal = Signal.deserialize(msg.payload)
            context.workbook = signal.data
        if context.workbook:
            if not context.is_ready():
                # get context from server
                request = Message.request(Request.getcontext(context.workbook))
                return request, State.WaitingContext
            else:
                return None, State.WaitingEvent
        return None, self


class WaitingContext:
    """
    Waiting context from server
    """
    def next(self, context, msg):
        if msg.is_response():
            response = Response.deserialize(msg.payload)
            context.loads(response.data)
        if context.is_ready():
            return None, State.Ready
        return None, self


class Ready:
    """
    Context is ready

    Test: Cell A3 changed -> Change cell B3
          Cell A5 changed -> Request cells B2:B4
    """
    def next(self, context, msg):
        if msg.is_event():
            event = Event.deserialize(msg.payload)
            if event.type == Event.Type.SheetChange:
                first_cell = event.cells[0][0]
                if first_cell.key == "$A$3":
                    cell = Cell("$B$3", "33", color=3, font="Times New Roman")
                    cell.bold = True
                    cell.underline = True
                    cell.borders.right = Border(Border.Weight.xlMedium,
                                                Border.LineStyle.xlContinuous)
                    cell.borders.bottom = Border(Border.Weight.xlThick,
                                                 Border.LineStyle.xlContinuous)
                    action = Action.change_from_event(event, [[cell]])
                    logger.debug("Action JSON is sent to A3")
                    return Message.action(action), self
                if first_cell.key == "$A$5":
                    action = Action.request_from_event(event, "$B$2:$B$4")
                    logger.debug("Request JSON is sent for B2:B4")
        return None, self


State.WaitingWorkbookID = WaitingWorkbookID()
State.WaitingContext = WaitingContext()
State.Ready = Ready()


class Runtime:
    def __init__(self):
        self.currentState = State.WaitingWorkbookID
        self.context = Context()

    def run(self, message):
        logger.debug("state before: %s", self.currentState.__class__.__name__)
        with self.context as context:
            answer, self.currentState = \
                self.currentState.next(context, message)
            logger.debug(
                "state after: %s", self.currentState.__class__.__name__)
            return answer
