"""
THE IMPORT ORDER MATTERS!!
    Input widgets rely on Tab Shoji
    ColorWidget relies on user input widgets

    I need more abstract classes...
"""

""" IMPORT ABSTRACT WIDGETS """
from .AbstractWidgets import *

""" MODEL VIEW WIDGET"""
from .ModelViewWidget import ModelViewWidget as ModelViewWidget

""" TANSU """
from .ShojiWidget import ShojiModelItem as ShojiModelItem
from .ShojiWidget import ShojiModel as ShojiModel

from .ShojiWidget import ShojiModelViewWidget as ShojiModelViewWidget
from .ShojiWidget import ShojiModelDelegateWidget as ShojiModelDelegateWidget

""" INPUT WIDGETS """
from .InputWidgets import *

# color widget
from .InputWidgets.ColorInputWidget import ColorGradientDelegate as ColorGradientDelegate
from .InputWidgets.ColorInputWidget import ColorInputWidget as ColorInputWidget

""" NODE WIDGETS """
from .NodeWidgets import NodeTypeListWidget
# from .NodeTreeWidget import NodeTreeMainWidget
# old stuff
from .LibraryWidget import LibraryWidget as LibraryWidget
from .LadderWidget import LadderWidget as LadderWidget

from .__utils__ import *
