
import sys


# os.environ['QT_API'] = 'pyside2'
from qtpy import API_NAME
print(API_NAME)
#import PySide2
#print(PySide2.__version__)
from qtpy.QtWidgets import (QApplication, QWidget, QLabel)
from cgwidgets.widgets import PiPDisplayWidget, AbstractPopupBarWidget
from cgwidgets.utils import centerWidgetOnCursor, setAsAlwaysOnTop, getDefaultSavePath
from cgwidgets.settings import attrs

app = QApplication(sys.argv)

widget = PiPDisplayWidget()

widget.setEnlargedScale(0.75)
widget.setPiPScale(0.25)
widget.setDisplayMode(AbstractPopupBarWidget.PIPTASKBAR)

#widget.setDirection(attrs.NORTH)
for x in range(3):
    label = QLabel(str(x))
    widget.createNewWidget(label, name=str(x))
widget.setIsDisplayNamesShown(True)
setAsAlwaysOnTop(widget)
widget.show()
widget.resize(512,512)
centerWidgetOnCursor(widget)
sys.exit(app.exec_())
