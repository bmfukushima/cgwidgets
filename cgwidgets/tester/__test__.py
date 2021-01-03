import unittest
import sys
import os
import platform

import qtpy
from qtpy.QtWidgets import QApplication
from qtpy.QtCore import __version__

from cgwidgets.widgets import __test__ as test_widgets
from cgwidgets.delegates import __test__ as test_delegates


def testDelegates():
    test_delegates.mainFunction()


def testWidgets():
    test_widgets.mainFunction()


def mainFunction():
    # print header
    print(
        """
####################################################################
####################################################################
                QT_API    == {0}
                Version   == {1}
                Python    == {2}
####################################################################
        """.format(
            qtpy.API,
            __version__,
            platform.python_version()
            )
    )

    # run unit test
    app = QApplication(sys.argv)
    testDelegates()
    testWidgets()

    # print closer
    print("""

END

    """)


if __name__ == '__main__':
    print(
    """
    QT_API == {}
    """.format(qtpy.API)
    )

    app = QApplication(sys.argv)
    testDelegates()
    testWidgets()
