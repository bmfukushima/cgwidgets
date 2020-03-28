import unittest
import sys

from qtpy.QtWidgets import QApplication, QLineEdit
from qtpy.QtGui import QCursor, QMouseEvent
from qtpy.QtTest import QTest
from qtpy.QtCore import Qt, QEvent, QPoint

from cgwidgets.utils import installLadderDelegate
from cgwidgets.delegates.LadderDelegate.LadderDelegate import LadderItem


class TestLadderDelegate(unittest.TestCase):
    '''
    # install delegate
    # click / drag
    '''
    @classmethod
    def setUpClass(cls):
        TestLadderDelegate.parent_widget = TestParentWidget()
        TestLadderDelegate.ladder_delegate = TestLadderDelegate.parent_widget.ladder
        TestLadderDelegate.ladder_delegate.setValue(3)
        app.processEvents()

    def setValue(self, value):
        TestLadderDelegate.ladder_delegate.setValue(value)
        self.assertEqual(TestLadderDelegate.ladder_delegate.middle_item.getValue(), value)

    def test_setValue(self):
        self.setValue(5)

    def userClickDrag(self):
        '''
        Tests a user click/drag operation.  When the delegate opens, a user
        can click + drag on a value to determine how much to update the
        parent widget.
        '''
        from decimal import Decimal, getcontext

        item_list = TestLadderDelegate.ladder_delegate.item_list

        for item in item_list:
            if isinstance(item, LadderItem):
                # pen down
                QTest.mousePress(item, Qt.LeftButton)

                # pen move
                num_ticks = 0
                for x in range(0, 343):
                    pos = QPoint(QCursor().pos().x() + x, QCursor().pos().y() + x)
                    move_event = QMouseEvent(
                        QEvent.MouseMove,
                        pos,
                        Qt.LeftButton,
                        Qt.LeftButton,
                        Qt.KeyboardModifiers()
                    )
                    item.mouseMoveEvent(move_event)

                    # do math for test
                    magnitude = LadderItem._LadderItem__getMagnitude(item, QCursor().pos(), pos)
                    if num_ticks != int(magnitude):
                        # set significant digits
                        sig_digits = item.parent()._significant_digits
                        int_len = len(item.parent().middle_item.text().split('.')[0])
                        getcontext().prec = sig_digits + int_len
                        value_mult = item.value_mult * num_ticks

                        # get values
                        return_val = Decimal(value_mult) + item.orig_value
                        current_val = item.parent().middle_item.getValue()

                        # update num ticks
                        num_ticks = int(magnitude)

                    # test values
                    try:
                        self.assertEqual(float(return_val), float(current_val))
                    except UnboundLocalError:
                        # pass on the first run since the values are not set yet
                        pass

                # pen up
                QTest.mouseRelease(item, Qt.LeftButton)

    def test_userClickDrag(self):
        self.userClickDrag()


class TestParentWidget(QLineEdit):
    def __init__(self, parent=None, value=0):
        super(TestParentWidget, self).__init__(parent)
        #pos = QCursor().pos()
        #self.setGeometry(pos.x(), pos.y(), 200, 100)
        value_list = [0.001, 0.01, 0.1, 1, 10, 100, 1000]

        #pos = QCursor.pos()
        self.ladder = installLadderDelegate(
            self,
            user_input=QEvent.MouseButtonPress,
            value_list=value_list
        )

    def setValue(self, value):
        self.setText(str(value))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    unittest.main()