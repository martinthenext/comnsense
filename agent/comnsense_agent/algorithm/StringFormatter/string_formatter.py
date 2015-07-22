from .transformer import StringTransformer
# TODO import EventHander

class StringFormatter(EventHander):
    """
    StringFormatter autoformats a sequence of edits.
    Edit - a cell change there previous value is not empty

    Wait for any edit which is not just a number
    Train a StringTransformer on the change
    If the next edit is in the same column:
        Apply the trained formatter on the prev value
        If the result == new value, you confirmed StringFormatter does it right
    Apply
    
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
        ConfirmedRequestedCell = 2

        # Receive the requested cell.
        # If it's empty erase all infos and go to AwaitingFirstEdit
        # If it's not empty reformat the cell and request a new cell

    def __init__(self):
        # The state of the formatter is the index of column 
        self.transformer = None
        self.column_index = None
    
    def handle(event, context):
        pass
       
