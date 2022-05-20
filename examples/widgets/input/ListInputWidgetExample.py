import sys
from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
from qtpy.QtGui import QCursor

from cgwidgets.widgets import ListInputWidget, AbstractListInputWidget
from cgwidgets.views.CompleterView import CompleterPopup


app = QApplication(sys.argv)


class TestSubclass(ListInputWidget):
    """
    Drop down menu with autocomplete for the user to select
    what GSV that they wish for the Variable Manager to control
    """
    def __init__(self, parent=None):
        """
        @exists: flag used to determine whether or not the popup menu for the GSV change
                            should register or not (specific to copy/paste of a node)
        """
        super(TestSubclass, self).__init__(parent)
        # setup attrs
        self.setUserFinishedEditingEvent(self.userFinishedEditingA)
        self.populate(self.getAllVariables())
        self.setCleanItemsFunction(self.getAllVariables)
        self.dynamic_update = True
        self.filter_results = False

    """ UTILS """
    def getAllVariables(self):
        return [['a', (255, 0, 0, 255)], ['b'], ['c'], ['aa'], ['bb'], ['cc'], ['b1'], ['c1'], ['aaa'], ['bbb'], ['ccc']]

    def userFinishedEditingA(self, widget, value):
        print('---- FINISH EVENT ----')
        print(widget, value)


def userFinishedEditing(widget, value):
    print('---- FINISH EVENT ----')
    print(widget, value)

    #qApp.processEvents()
    #QApplication.instance().processEvents()
    #widget.setText('')

w = QWidget()
l = QVBoxLayout(w)
def cleanItems():
    return [['a', (255, 0, 0, 255)], ['b'], ['c'], ['aa'], ['bb'], ['cc'], ['b1'], ['c1'], ['aaa'], ['bbb'], ['ccc']]
list_widget = TestSubclass()
list_widget.setUserFinishedEditingEvent(userFinishedEditing)
list_widget.setCleanItemsFunction(cleanItems)
list_widget.dynamic_update = True
# list_widget.filter_results = False


list_widget.display_item_colors = True


e = CompleterPopup()
l.addWidget(list_widget)
l.addWidget(e)
e.setModel(list_widget.proxy_model)

# item_list = ['a', 'b', 'c', 'aa', 'bb', 'cc']
# w=QListView()
# w.setStyleSheet("""
#     QListView::item:selected{background-color: rgba(255,0,0,255);}
# """)
# model = CustomModel(item_list=item_list)
# w.setModel(model)

weiner = TestSubclass()
weiner = AbstractListInputWidget(item_list=[['a', (255, 0, 0, 255)], ['b'], ['c'], ['aa'], ['bb'], ['cc'], ['b1'], ['c1'], ['aaa'], ['bbb'], ['ccc']])
from cgwidgets.widgets import LabelledInputWidget, ShojiLayout
test_labelled = LabelledInputWidget(name="test", delegate_widget=weiner)

test_labelled.setUserFinishedEditingEvent(userFinishedEditing)
l.addWidget(test_labelled)

# test_shoji = ShojiLayout()
# test_shoji.addWidget(weiner)
# l.addWidget(test_shoji)


w.show()
w.move(QCursor.pos())
sys.exit(app.exec_())