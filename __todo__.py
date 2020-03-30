"""
Unit Tests:
    - Delegates seems to be working
    - Move tests to main...
    - Add widgets in
    - Run pyside2/PyQt5 tests
        Update to Python 3.5 --> 3.8

        Setup checks for Python 2.7
            * pyside
            * pyqt4


Widgets:
    - Ladder Delegate / Widget
        - widget just installs the delegate on:
            line edit
            label

    - Error on PySide for ColorWidget
    File "/media/ssd01/Scripts/WidgetFactory/cgwidgets/widgets/ColorWidget/ColorWidget.py", line 702, in _pickColor
    screen = QApplication.primaryScreen()
AttributeError: type object 'PySide.QtGui.QApplication' has no attribute 'primaryScreen'

    - Split out image widget

    - Split out view widgets

Notes:
    * Unit tests run in script mode
"""
