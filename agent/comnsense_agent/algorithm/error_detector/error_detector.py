import logging
import operator

from ..event_handler import EventHandler
from .column_error_detector import ColumnErrorDetector
from comnsense_agent.data import Event

logger = logging.getLogger(__name__)


class ErrorDetector(EventHandler):
    def __init__(self):
        self.columns = {}

    def handle(self, event, context):
        # waiting header, nothing to do
        if context.lookup(event.sheet).get_header() is None:
            return []

        answer = {}

        # initialize algorithm for all columns in header
        for column in context.lookup(event.sheet).get_header_columns():
            if column not in self.columns:
                logger.debug("initialize column: %s", column)
                self.columns[column] = ColumnErrorDetector(column)
                answer[column] = []
                answer[column] += \
                    self.columns[column].handle(
                        self.normalize_event(event, context, column), context)

        for column in event.columns:
            if column not in self.columns:
                logger.warn("column %s is not in header, skip ...", column)
                continue

            # initilizing actions already in answer
            if column in answer:
                continue

            logger.debug("column: %s", column)
            answer[column] = []
            answer[column] += self.columns[column].handle(
                    self.normalize_event(event, context, column), context)

        return reduce(operator.add, answer.values(), [])

    @staticmethod
    def normalize_event(event, context, column):
        cells = []
        prev_cells = []

        for cell in event.columns.get(column, []):
            # skip cells from header
            if cell.row in context.lookup(event.sheet).get_header_rows():
                continue

            cells.append([cell])

        if event.prev_columns.get(column):
            for cell in cells:
                prev = [c for c in event.prev_columns.get(column)
                        if c.key == cell[0].key] or [None]
                prev_cells.append(prev)

        return Event(event.type, event.workbook,
                     event.sheet, cells, prev_cells)
