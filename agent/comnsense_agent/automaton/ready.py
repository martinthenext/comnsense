import logging

from comnsense_agent.message import Message
from comnsense_agent.data import Event, Action, Request, Signal, Response
from comnsense_agent.data import Cell, Border

from comnsense_agent.context import Sheet, Table

from comnsense_agent.automaton import State

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

            table = Table(sheet)
            context.sheets[event.sheet].tables.append(table)

            if not table.header:
                response = table.header_response()
                context.return_state = self
                return response, State.WaitingHeader

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
                    action = Action.request_from_event(event, "$B$2:$B$4", Action.Flags.RequestColor)
                    logger.debug("Request JSON is sent for B2:B4")
                    return Message.action(action), self

            if event.type == Event.Type.RangeResponse:
                logger.debug("Received RangeResponse")
                logger.debug(str(event.cells))
                if event.cells[1][0].color == 3:
                    cell = Cell("$D$3", "44", color=2)
                    action = Action.change_from_event(event, [[cell]])
                    return Message.action(action), self

        return None, self
