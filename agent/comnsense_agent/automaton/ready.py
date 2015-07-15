import logging

from comnsense_agent.algorithm.laptev import OnlineQuery
from comnsense_agent.automaton import State
from comnsense_agent.context import Sheet, Table
from comnsense_agent.data import Cell, Border
from comnsense_agent.data import Event, Action, Request, Signal, Response
from comnsense_agent.message import Message

logger = logging.getLogger(__name__)


class Ready:
    """
    Context is ready
    """
    def next(self, context, msg):
        if msg.is_event():
            event = Event.deserialize(msg.payload)
            if event.sheet not in context.sheets:
                sheet = Sheet(context, event.sheet)
                context.sheets[event.sheet] = sheet
            else:
                sheet = context.sheets[event.sheet]

            # TODO assuming that just one table on sheet
            if context.sheet[event.sheet].tables:
                table = context.sheets[event.sheet].tables[0]
            else:
                table = Table(sheet)
                context.sheets[event.sheet].tables.append(table)

            if table.header is None:
                response = table.request_header()
                context.return_state = self
                return response, State.WaitingHeader

            if event.type in (Event.Type.SheetChange,
                              Event.Type.RangeResponse):
                algorithm = OnlineQuery()
                return algorithm.query(context, event), self

        return None, self
