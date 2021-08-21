from qtpy.QtWidgets import QSplitter
from qtpy.QtCore import Qt, QTimer

class AbstractSplitterWidget(QSplitter):
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
    def __init__(self, orientation=Qt.Vertical, parent=None):
        super(AbstractSplitterWidget, self).__init__(orientation, parent)
        self._delayed_splitter_moved_events_data = {}
        self._is_frozen = False

        self.splitterMoved.connect(self.splitterMovedEvent)

    """ EVENTS """
    def splitterMovedEvent(self):
        """ Runs all of the delayed events after the user finishes moving the splitter"""

        # preflight
        if self.isFrozen(): return

        # Delayed Events Handler
        for name, event_data in self.delayedSplitterMovedEventsData().items():
            if hasattr(self, "{name}_timer".format(name=name)):
                getattr(self, "{name}_timer".format(name=name)).setInterval(event_data["delay"])
            else:
                timer = QTimer()
                timer.start(event_data["delay"])
                event = getattr(self, "{name}_event".format(name=name))
                timer.timeout.connect(event)
                setattr(self, "{name}_timer".format(name=name), timer)

    """ PROPERTIES """
    def delayedSplitterMovedEventsData(self):
        return self._delayed_splitter_moved_events_data

    def isFrozen(self):
        return self._is_frozen

    def setIsFrozen(self, is_frozen):
        self._is_frozen = is_frozen

    """ UTILS """
    def delayedSplitterMovedEventNames(self):
        """ Returns a list of strings of all of the delayed move events """
        return list(self.delayedSplitterMovedEventsData().keys())

    def changeDelayedEventName(self, old_name, new_name):
        if old_name in self.delayedSplitterMovedEventNames():
            self.delayedSplitterMovedEventsData()[new_name] = self.delayedSplitterMovedEventsData().pop(old_name)
        else:
            print("{old_name} is not valid".format(old_name=old_name))
        pass

    def setEventDelayAmount(self, name, delay_amount):
        """ Sets the delay amount of the event provided

        Args:
            name (str):
            delay_amount (int):
        """

        self.delayedSplitterMovedEventsData()[name]["delay"] = delay_amount

    """ DELAYED SPLITTER MOVED"""
    def addDelayedSplitterMovedEvent(self, name, delayed_splitter_moved_function, delay_amount=50):
        """The function provided will be run after a certain amount of time (delay_amount) after the splitter has been moved

        Args:
            delay_amount (int): number of milliseconds to wait before running the function
            delayed_splitter_moved_function (function): Function that will run after the resize has finished
            name (str): name of event
        """
        self.delayedSplitterMovedEventsData()[name] = {}
        self.delayedSplitterMovedEventsData()[name]["delay"] = delay_amount

        # create event
        def splitterFinishedMoving():
            delayed_splitter_moved_function()
            delattr(self, "{name}_timer".format(name=name))

        setattr(self, "{name}_event".format(name=name), splitterFinishedMoving)

    def removeDelayedSplitterMovedEvent(self, name):
        del self.delayedSplitterMovedEventsData()[name]
        delattr(self, "{name}_event".format(name=name))

    def removeAllDelayedSplitterMovedEvents(self):
        """ Removes all of the delayed splitter events """
        for event_name in self.splitterMovedEvent():
            self.removeDelayedSplitterMovedEvent(event_name)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QLabel
    from cgwidgets.utils import setAsAlwaysOnTop, centerWidgetOnCursor
    app = QApplication(sys.argv)

    def delayEvent1():
        print('1')

    def delayEvent2():
        print('2')

    def delayEvent3():
        print('3')

    splitter = AbstractSplitterWidget(Qt.Horizontal)
    for x in range(3):
        label = QLabel("test")
        splitter.addWidget(label)

    splitter.addDelayedSplitterMovedEvent("one", delayEvent1, 100)
    splitter.addDelayedSplitterMovedEvent("two", delayEvent2, 200)
    splitter.addDelayedSplitterMovedEvent("three", delayEvent3, 300)

    splitter.removeDelayedSplitterMovedEvent("three")

    setAsAlwaysOnTop(splitter)
    splitter.show()
    centerWidgetOnCursor(splitter)


    sys.exit(app.exec_())