import sys
import os
os.environ['QT_API'] = 'pyside2'
from cgwidgets.widgets import AbstractModelViewWidget

class ModelViewWidget(AbstractModelViewWidget):
    def __init__(self, parent=None):
        super(ModelViewWidget, self).__init__(parent)


if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication, QTreeView, QWidget, QVBoxLayout
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)

    # create event functions
    #
    def testDelete(item):
        print("DELETING --> -->", item.columnData()['name'])

    def testDrag(items, model):
        print("DRAGGING -->", items)
        print(items)

    def testDrop(data, items, model, row, parent):
        print("DROPPING -->", row, items, parent)

    def testEdit(item, old_value, new_value):
        print("EDITING -->", item, old_value, new_value)
    #
    def testEnable(item, enabled):
        print("ENABLING -->", item.columnData()['name'], enabled)
    #
    def testSelect(item, enabled):
        print("SELECTING -->", item.columnData()['name'], enabled)
    #
    def testDelegateToggle(event, widget, enabled):
        print('toggle joe')

    main_widget = ModelViewWidget()

    # main_widget.setPresetViewType(ModelViewWidget.TREE_VIEW)
    view = QTreeView()
    model = main_widget.model()

    #
    # # insert indexes
    for x in range(0, 4):
        index = main_widget.model().insertNewIndex(x, name=str('node%s'%x))
        for i, char in enumerate('no0'):
            main_widget.model().insertNewIndex(i, name=char*3, parent=index)

    main_widget.setIndexSelectedEvent(testSelect)
    # test filter
    # TODO FILTER TEST
    view.setModel(model)


    w = QWidget()
    l = QVBoxLayout(w)
    l.addWidget(main_widget)
    l.addWidget(view)

    # # # create delegates
    # delegate_widget = QLabel("F")
    # main_widget.addDelegate([Qt.Key_F], delegate_widget)
    #
    # delegate_widget = QLabel("Q")
    # main_widget.addDelegate([Qt.Key_Q], delegate_widget)
    #
    # #
    # # # set model event
    # main_widget.setDragStartEvent(testDrag)
    # main_widget.setDropEvent(testDrop)
    # main_widget.setTextChangedEvent(testEdit)
    # main_widget.setItemEnabledEvent(testEnable)
    # main_widget.setItemDeleteEvent(testDelete)
    # main_widget.setIndexSelectedEvent(testSelect)
    # main_widget.setDelegateToggleEvent(testDelegateToggle)
    # #
    # # # set flags
    # main_widget.setIsRootDropEnabled(True)
    # main_widget.setIsEditable(True)
    # main_widget.setIsDragEnabled(True)
    # #main_widget.setIsDropEnabled(True)
    # main_widget.setIsEnableable(True)
    # main_widget.setIsDeleteEnabled(True)
    #
    # # set selection mode
    # main_widget.setMultiSelect(True)



    w.move(QCursor.pos())

    w.show()




    sys.exit(app.exec_())