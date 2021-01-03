"""
THE IMPORT ORDER MATTERS!!
    Input widgets rely on Tab Tansu
    ColorWidget relies on user input widgets

    I need more abstract classes...
"""

""" IMPORT ABSTRACT WIDGETS """
from .AbstractWidgets import *

""" TANSU """
from .TansuWidget import TansuModelItem as TansuModelItem
from .TansuWidget import TansuModel as TansuModel

from .TansuWidget import TansuBaseWidget as TansuBaseWidget
from .TansuWidget import TansuModelViewWidget as TansuModelViewWidget
from .TansuWidget import TansuHeaderListView as TansuHeaderListView
from .TansuWidget import TansuHeaderTreeView as TansuHeaderTreeView
from .TansuWidget import TansuModelDelegateWidget as TansuModelDelegateWidget

""" INPUT WIDGETS """
from .InputWidgets import *

# color widget
from .InputWidgets.ColorInputWidget import ColorGradientDelegate as ColorGradientDelegate
from .InputWidgets.ColorInputWidget import ColorInputWidget as ColorInputWidget

# old stuff
from .LibraryWidget import LibraryWidget as LibraryWidget
from .LadderWidget import LadderWidget as LadderWidget

from .__utils__ import *
