import logging


from comnsense_agent.message import Message
from comnsense_agent.data import Event, Action, Request, Signal, Response

from comnsense_agent.automaton import State

logger = logging.getLogger(__name__)


class WaitingHeader:
    def next(self, context, msg):
        if msg.is_event():
            event = Event.deserialize(msg.payload)
            if event.type == Event.Type.RangeResponse:
                # assuming that header does not contain empty values
                # so, search for first empty value
                # all cells before is header
                header = event.cells[0]
                mask = [True if cell.value else False for cell in header]
                try:
                    empty = mask.index(False)
                except ValueError:
                    empty = -1
                # assuming that just one table on sheet
                # TODO fix it
                table = context.sheets[event.sheet].tables[0]
                if empty < 0:  # not found
                    logger.debug("cound not found empty value")
                    if table.header is None:
                        table.header = header
                    else:
                        table.header += header
                    # TODO return request for next part
                    state = context.return_state
                    context.return_state = None
                    return None, state
                elif empty == 0 and not table.header:
                    logger.warn("no header in table")
                    state = context.return_state
                    context.return_state = None
                    # TODO think about it, what if sheet is actually ugly
                    return None, state
                else:
                    if table.header is None:
                        table.header = header[:empty]
                    else:
                        table.header += header[:empty]
                    state = context.return_state
                    context.return_state = None
                    return None, state
            else:
                return None, self

        else:
            return None, self
