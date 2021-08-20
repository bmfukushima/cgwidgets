"""
TODO:
    BUGS:
        DragDelegate...
            Cannot have the following hierarchy
                ShojiLayout --> ShojiLayouter --> LabelledInputWidget --> Ladder
                The invisible drag on the ladder for some reason gets bricked, and the invisible
                widget is displayed as a giant black square...
            AbstractPiPOrganizerWidget also bjorking...
                DragDelegate appeares to be somehow showning the new widget???


    CLEANUP:
        settings
            import settings.module
                or
            from settings import thingy

* All imports...
    need to register to import from cgwidgets.
    needs to assume that this lib is in the pythonpath

* Additional Libs
    qtpy
    PySide2
    shiboken2
    shiboken2_generator
    Pillow
Unit Tests:
    * Python 3.7.11 / 3.8.10
        - PySide 5.15.2
        - PyQt 5.15.2
            * /usr/lib/python2.7/dist-packages
                need to reinstall this... because pip doesnt want to install it =\


    * How to run tests in different environments...
        bash script...



Widgets:
    - Error on PySide for ColorWidget
    File "/media/ssd01/Scripts/WidgetFactory/cgwidgets/widgets/ColorWidget/ColorWidget.py", line 702, in _pickColor
    screen = QApplication.primaryScreen()
AttributeError: type object 'PySide.QtGui.QApplication' has no attribute 'primaryScreen'
    - Split out image widget
    - Split out view widgets

Notes:
    * Unit tests run in script mode
"""
