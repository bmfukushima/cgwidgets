from qtpy.QtCore import Qt

from cgwidgets.widgets import AbstractSplitterWidget


class SplitterWidget(AbstractSplitterWidget):
    """ QSplitter with additional functionality

    Adding a delayed splitter move event.  This will make it so that when
    functions run with the "splitterMoved" will happen after a certain amount
    of delay after the splitter has stopped moving.

    DelayedSplitterMoved:
        Everytime a delayed splitter moved event is added (addDelayedSplitterMovedEvent),
        a new function will be created in the class under the name "{name_event}".  Which will
        be called after a certain amount of delay.

        In order for each event to be unique, a name must be provided.  Note that this is also
        the same name that will be used to remove the event later

    Attributes:
        delayed_resize_data (dict): data of all of the delayed events
            {name_of_event (str) : {
                delay (str) : delay_amount (int)}
            }
        is_frozen (bool):

    """
    def __init__(self, parent=None, orientation=Qt.Vertical):
        super(SplitterWidget, self).__init__(parent, orientation)


