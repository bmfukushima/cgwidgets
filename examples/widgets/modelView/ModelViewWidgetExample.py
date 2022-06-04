import sys
import os
os.environ['QT_API'] = 'pyside2'
from qtpy.QtWidgets import QApplication

from cgwidgets.widgets import ModelViewWidget, StringInputWidget
from cgwidgets.utils import centerWidgetOnCursor

if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()


class ModelViewWidgetSubclass(ModelViewWidget):
    def __init__(self, parent=None):
        super(ModelViewWidgetSubclass, self).__init__(parent)

        # setup view
        # this can also be set to ModelViewWidget.LIST_VIEW
        self.setPresetViewType(ModelViewWidget.TREE_VIEW)
        self.setHeaderData(["name"])

        # insert new index
        for x in range(0, 4):
            index = self.insertNewIndex(x, name=str('node%s' % x))

            self.insertNewIndex(0, parent=index, column_data={"name":"a", "test":"f"})
            self.insertNewIndex(0, parent=index, column_data={"name":"b", "test":"a"})
            self.insertNewIndex(0, parent=index, column_data={"name":"c", "test":"f"})

        self.setDragStartEvent(self.customDragStartEvent)
        self.setDropEvent(self.customDropEvent)
        self.setTextChangedEvent(self.customEditEvent)
        self.setItemEnabledEvent(self.customEnableEvent)
        self.setItemDeleteEvent(self.customDeleteEvent)
        self.setIndexSelectedEvent(self.customSelectEvent)

        self._create_new_item_widget = StringInputWidget()
        self._create_new_item_widget.setUserFinishedEditingEvent(self.createNewItemEvent)
        self.addDelegate([], self._create_new_item_widget, always_on=True)
        # self._create_new_item_widget.show()

    def createNewItemEvent(self, widget, value):
        if value:
            index = len(self.rootItem().children())
            self.insertNewIndex(index, column_data={"name": value, "test": "f"})
            widget.setText("")
            print(widget, value)

    def customDeleteEvent(self, item):
        print("DELETING --> -->", item.columnData()['name'])

    def customDragStartEvent(self, items, model):
        print("DRAGGING -->", items, model)

    def customDropEvent(self, data, items, model, row, parent):
        print("""
    DROPPING -->
        data --> {data}
        row --> {row}
        items --> {items}
        model --> {model}
        parent --> {parent}
            """.format(data=data, row=row, model=model, items=items, parent=parent)
              )

    def customEditEvent(self, item, old_value, new_value, column):
        print("EDITING -->", item, old_value, new_value)

    def customEnableEvent(self, item, enabled):
        print("ENABLING -->", item.columnData()['name'], enabled)

    def customSelectEvent(self, item, enabled):
        print("SELECTING -->", item.columnData()['name'], enabled)

    def customDelegateToggleEvent(self, enabled, event, widget):
        print("TOGGLING -{key}->".format(key=event.key()), widget, enabled)

main_widget = ModelViewWidgetSubclass()

# show widget
main_widget.show()
main_widget.resize(1920, 1080)
centerWidgetOnCursor(main_widget)

sys.exit(app.exec_())