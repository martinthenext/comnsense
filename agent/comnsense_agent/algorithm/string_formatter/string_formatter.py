from .transformer import StringTransformer
# TODO import EventHander
from comnsense.data import Action

class StringFormatter(EventHander):
    """
    StringFormatter autoformats a sequence of edits.
    Edit - a cell change there previous value is not empty
    """

    class State:
        # Wait for any edit where the new value is not a number
        AwaitingFirstEdit = 0

        # Train a StringTransformer on the edit and wait for a next edit
        AwaitingSecondEdit = 1

        # If the second edit is in the same column
        # try predicting the new value from the old one
        # If didn't work erase all infos and go back to AwaitingFirstEdit
        # If worked the transformation is confirmed
        # Request a cell under the last edit
        ConfirmedChangingCells = 2

        # Receive the requested cell.
        # If it's empty erase all infos and go to AwaitingFirstEdit
        # If it's not empty reformat the cell and request a new cell

    def __init__(self):
        self.start_over()
    
    def start_over(self):
        self.transformer = None
        self.prev_edit_column = None
        self.prev_edit_row_index = None
        self.state = StringFormatter.State.AwaitingFirstEdit

    def is_numeric(value):
        """
        Check if a value is an int, float or a string repr of those

        >>> is_numeric(42)
        True
        >>> is_numeric('42.3')
        True
        >>> is_numeric('42.LOL')
        False
        """
        
        try:
            float(value)
            return True
        except ValueError:
            return False

    def handle(event, context):
        # In any state, we are only interested in single cell events
        if len(event.cells) > 1:
            return
        if len(event.cells[0]) > 1:
            return
        cell = event.cells[0][0]

        # Also, in any state we are only insterested in edits
        # If user is adding new values and not editing we start over
        if not event.prev_cells:
            return

        prev_cell = event.prev_cells[0][0]
        if not prev_cell.value:
            self.start_over()
            return

        if self.is_numeric(cell.value):
            self.start_over()
            return

        if self.state == StringFormatter.State.AwaitingFirstEdit:
            self.transformer = StringTransformer()
            self.transformer.train_by_example(prev_cell.value, cell.value)
            
            self.prev_edit_column = cell.column
            self.prev_edit_row_index = int(cell.row)
            
            self.state = StringFormatter.State.AwaitingSecondEdit 
            return

        if self.state == StringFormatter.State.AwaitingSecondEdit:
            # TODO we only work with edits going down one column
            if cell.column != self.prev_edit_column:
                self.start_over()
                return

            row_index = int(cell.row)
            if row_index != self.prev_edit_row_index + 1:
                self.start_over()
                return

            guess = self.transformer.transform(prev_cell.value)
            if guess == cell.value:
                # We confirmed we guess right, now let's do all cells
                # down till we run into the empty one
                row_to_request = row_index + 1
                range_to_request = "$%s$%s" % (cell.column, row_to_request)
                action = Action(
                        Action.Type.RangeRequest,
                        event.workbook,
                        event.sheet,
                        range_to_request
                )
                
                self.state = StringFormatter.State.ConfirmedChangingCells
                return [ action ]

            else:
                # We didn't guess
                self.start_over()
                return
        
        if self.state == StringFormatter.State.ConfirmedChangingCells:
            # We have ordered a value of a cell, see it it's empty
            if not cell.value:
                self.start_over()

            # It has a value, transform it and push it back
            new_value = self.transformer.transform(cell.value)
            cell.value = new_value

            change_action = Action(
                    Action.Type.ChangeCell,
                    event.workbook,
                    event.sheet,
                    [[ cell ]]
            )

            # Request a new cell further down
            row_to_request = int(cell.row) + 1
            range_to_request = "$%s$%s" % (cell.column, row_to_request)
            request_action = Action(
                    Action.Type.RangeRequest,
                    event.workbook,
                    event.sheet,
                    range_to_request
            )

            return [ change_action, request_action ]
 
