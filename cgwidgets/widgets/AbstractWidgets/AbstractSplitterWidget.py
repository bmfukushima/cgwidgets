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
            {name_of_event (str) : event_data (DelayedSplitterMovedEventData)}
        is_frozen (bool):

    """
    def __init__(self, parent=None, orientation=Qt.Vertical):
        super(AbstractSplitterWidget, self).__init__(orientation, parent)
        self._delayed_splitter_moved_events_data = {}
        self._is_frozen = False

        self.splitterMoved.connect(self.splitterMovedEvent)

    """ EVENTS """
    def splitterMovedEvent(self, pos, index):
        """ Runs all of the delayed events after the user finishes moving the splitter"""

        # preflight
        if self.isFrozen(): return

        # Delayed Events Handler
        for name, event_data in self.delayedSplitterMovedEventsData().items():
            # if timer is running, reset it
            if hasattr(event_data, "_timer"):
                getattr(event_data, "_timer").setInterval(event_data.delayAmount())

            # if no timer, setup a new timer from the event data
            else:
                # setup timer
                timer = QTimer()
                timer.start(event_data.delayAmount())
                timer.timeout.connect(event_data.splitterFinishedMoving)

                # setup event data
                event_data.setPos(pos)
                event_data.setIndex(index)
                setattr(event_data, "_timer", timer)

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
        """ Changes the event name from the one provided to the new one

        Args:
            old_name (str):
            new_name (str):
        """
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
        self.delayedSplitterMovedEventsData()[name].setDelayAmount(delay_amount)

    """ DELAYED SPLITTER MOVED"""
    def addDelayedSplitterMovedEvent(self, name, delayed_splitter_moved_function, delay_amount=50):
        """The function provided will be run after a certain amount of time (delay_amount) after the splitter has been moved

        Args:
            delay_amount (int): number of milliseconds to wait before running the function
            delayed_splitter_moved_function (function): Function that will run after the resize has finished
            name (str): name of event
        """
        # self.delayedSplitterMovedEventsData()[name]["delay"] = delay_amount

        # create event
        # def splitterFinishedMoving(pos, index):
        #     delayed_splitter_moved_function(pos, index)
        #     delattr(self, "{name}_timer".format(name=name))

        self.delayedSplitterMovedEventsData()[name] = DelayedSplitterMovedEventData(
            name, delayed_splitter_moved_function, delay_amount)

        #setattr(self, "{name}_event".format(name=name), splitter_moved_object)

    def removeDelayedSplitterMovedEvent(self, name):
        del self.delayedSplitterMovedEventsData()[name]

    def removeAllDelayedSplitterMovedEvents(self):
        """ Removes all of the delayed splitter events """
        for event_name in self.splitterMovedEvent():
            self.removeDelayedSplitterMovedEvent(event_name)


class DelayedSplitterMovedEventData(object):

    def __init__(self, name, func, delay_amount):
        self._name = name
        self._function = func
        self._delay_amount = delay_amount
        self._index = 0
        self._pos = 0

    def delayAmount(self):
        return self._delay_amount

    def setDelayAmount(self, delay_amount):
        self._delay_amount = delay_amount

    def index(self):
        return self._index

    def setIndex(self, index):
        self._index = index

    def pos(self):
        return self._pos

    def setPos(self, pos):
        self._pos = pos

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def getFunction(self):
        return self._function

    def setFunction(self, func):
        self._function = func

    def splitterFinishedMoving(self):
        self.getFunction()(self.pos(), self.index())
        delattr(self, "_timer")


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QLabel
    from cgwidgets.utils import setAsAlwaysOnTop, centerWidgetOnCursor
    app = QApplication(sys.argv)

    def delayEvent1(pos, index):
        print(pos, index)
        print('1')

    def delayEvent2(pos, index):
        print(pos, index)
        print('2')

    def delayEvent3(pos, index):
        print(pos, index)
        print('3')

    splitter = AbstractSplitterWidget(orientation=Qt.Horizontal)
    for x in range(3):
        label = QLabel("test")
        splitter.addWidget(label)

    splitter.addDelayedSplitterMovedEvent("one", delayEvent1, 100)
    splitter.addDelayedSplitterMovedEvent("two", delayEvent2, 200)
    splitter.addDelayedSplitterMovedEvent("three", delayEvent3, 300)

    #splitter.removeDelayedSplitterMovedEvent("three")

    setAsAlwaysOnTop(splitter)
    splitter.show()
    centerWidgetOnCursor(splitter)


    sys.exit(app.exec_())