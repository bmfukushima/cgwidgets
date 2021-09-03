from qtpy.QtWidgets import QMenu, QVBoxLayout, QWidget
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt

from cgwidgets.utils import setAsTransparent, getCenterOfWidget, getCenterOfScreen, setAsTool

from AbstractScriptEditorWidgets import HotkeyDesignGUIWidget, GestureDesignGUIWidget

""" POPUP MENUS """
class PopupHotkeyMenu(QWidget):
    def __init__(self, parent=None, file_path=None, pos=None):
        super(PopupHotkeyMenu, self).__init__(parent)

        setAsTransparent(self)
        setAsTool(self)
        # set position
        y_size = 300
        x_size = y_size * 3
        if not pos:
            pos = getCenterOfScreen()

        self.setGeometry(
            int(pos.x() - x_size*.5),
            int(pos.y()-y_size*.5),
            x_size,
            y_size)

        # create layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        design_widget = HotkeyDesignGUIWidget(self, file_path=file_path, init_pos=pos)
        design_widget.setFocusPolicy(Qt.StrongFocus)
        design_widget.setFocus()
        main_layout.addWidget(design_widget)


class PopupGestureMenu(QWidget):
    def __init__(self, parent=None, file_path=None, pos=None):
        super(PopupGestureMenu, self).__init__(parent)
        """
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setWindowFlags(
            self.windowFlags()
            | Qt.NoDropShadowWindowHint
            | Qt.FramelessWindowHint
        )
        """
        setAsTransparent(self)
        setAsTool(self)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setStyleSheet("background-color:rgba(128,50,50, 255); border:none;")
        size = 200
        arbitrary_scaler = 5
        if not pos:
            pos = QCursor.pos()
        self.setGeometry(
            int(pos.x() - size * arbitrary_scaler * .5),
            int(pos.y() - size * arbitrary_scaler * .5),
            int(size * arbitrary_scaler),
            int(size * arbitrary_scaler)
        )
        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(0, 0, 0, 0)
        design_widget = GestureDesignGUIWidget(self, file_path=file_path, init_pos=pos, size=size)

        design_widget.setFocusPolicy(Qt.StrongFocus)
        design_widget.setFocus()

        main_layout.addWidget(design_widget)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)

    hotkey_file_path = "/media/ssd01/dev/katana/KatanaResources_old/Scripts/designs/7352456805894839296.Debug.json"
    popup_widget = PopupHotkeyMenu(file_path=hotkey_file_path)
    popup_widget.show()

    # gesture_file_path = "/media/ssd01/dev/katana/KatanaResources_old/Scripts/designs/7297414313744113664.GestureDesign.json"
    # gesture_widget = PopupGestureMenu(file_path=gesture_file_path)
    # gesture_widget.show()

    sys.exit(app.exec_())
