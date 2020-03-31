"""
Unit Tests:
    * Python 2.7.7
        - PySide 5.12
        - PyQt 5.12
            * /usr/lib/python2.7/dist-packages
                need to reinstall this... because pip doesnt want to install it =\


    * How to run tests in different environments...
        bash script...

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
