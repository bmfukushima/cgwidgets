import sys
from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from cgwidgets.widgets import ButtonInputWidget
from cgwidgets.settings import icons, iColor
from cgwidgets.utils import centerWidgetOnCursor

app = QApplication(sys.argv)

def updateScriptEvent(widget):
    if widget.is_script_dirty:
        widget.setTextBackgroundColor(iColor["rgba_gray_4"])
        print('dirty')
    if not widget.is_script_dirty:
        widget.setTextBackgroundColor(iColor["rgba_background_00"])
        print('not dirty')

    widget.is_script_dirty = not widget.is_script_dirty



# setup button
button_widget = ButtonInputWidget(
    user_clicked_event=updateScriptEvent, title="test", flag=False, is_toggleable=False)
button_widget.is_script_dirty = False
image_path = icons["update"]
button_widget.setImage(image_path)
button_widget.setFixedSize(128, 128)
# setup main widget
main_widget = QWidget()
main_layout = QVBoxLayout(main_widget)
main_layout.addWidget(button_widget)
main_layout.addWidget(QLabel('test'))
main_widget.show()
centerWidgetOnCursor(main_widget)
#button_widget.setFixedSize(256,256)

sys.exit(app.exec_())
