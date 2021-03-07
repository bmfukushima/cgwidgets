"""
This file contains the contents for creating a hover display on a widget.

This style sheet can be installed on any widget using the "installHoverDisplaySS()" method.

Different hover display options are available using the "HoverStyleSheet" class.
This class must be instantiated first, and then set the focus/hover/hover focus
portions of the style sheet.  Please note that these portions will automagically
be wrapped like:
    {type}:focus{focus_properties}{{
                {focus_ss}
    }}
"""

from cgwidgets.utils import attrs
from .colors import iColor
from .stylesheets import convertDictToCSSFlags, background_radial

""" UTILS """
def compileSSArgs(widget, hover_type_flags, hover_object):
    """
    Compiles a dictionary for all of the kwargs that will be used in the Style Sheet.

    Args:
        widget (QWidget): Widget that will have the style sheet install on it
        hover_type_flags (dict): of properties for each respective portion
            of the hover type
            {
                hover:{property:bool, property2:bool},
                hover_focus:{property:bool, property2:bool},
                focus:{property:bool}
            }

    Returns (kwargs): to be used in Style Sheet

    """
    # get default colors
    style_sheet_args = iColor.style_sheet_args

    # add dynamic properties
    style_sheet_args.update({
        'focus_properties':convertDictToCSSFlags(hover_type_flags['focus']),
        'hover_properties':convertDictToCSSFlags(hover_type_flags['hover']),
        'hover_focus_properties':convertDictToCSSFlags(hover_type_flags['hover_focus'])
    })

    # update colors
    style_sheet_args.update({
        "rgba_selected_hover": iColor["rgba_selected_hover"],
        "rgba_selected_background": iColor["rgba_selected_background"],
        "background_hover_radial": background_radial.format(
            rgba_background_00=iColor["rgba_background_00"],
            rgba_background_2=iColor["rgba_selected_background"]),
        "background_cancel_radial":background_radial.format(
            rgba_background_00=iColor["rgba_background_00"],
            rgba_background_2=iColor["rgba_cancel"]),
        "background_accept_radial":background_radial.format(
            rgba_background_00=iColor["rgba_background_00"],
            rgba_background_2=iColor["rgba_accept"]),
        "background_select_hover_radial":background_radial.format(
            rgba_background_00=iColor["rgba_background_00"],
            rgba_background_2=iColor["rgba_selected_hover"])
    })

    # add widget SS
    print(hover_object.hoverSS())
    style_sheet_args.update({
        'type': type(widget).__name__,
        'hover_ss': hover_object.hoverSS().format(**style_sheet_args),
        'focus_ss': hover_object.focusSS().format(**style_sheet_args),
        'hover_focus_ss': hover_object.focusSS().format(**style_sheet_args)
    })

    return style_sheet_args

class HoverStyleSheet(object):
    """
    Attributes:
        position (attrs.POSITION): the cardinal direction
        color (RGBA): 255 RGBA color to be displayed
        hover_style_type (HoverStyleSheet.HOVER_STYLE_TYPE)
            BORDER | BACKGROUND | RADIAL
                # todo finish setting up in __createStyleSheets
                    add conditional for hover_style_type
        border_style_type (HoverStyleSheet.BORDER_STYLE_TYPE): option to determine the border style type
            solid | dotted | dashed...
    """
    # HOVER STYLE TYPE
    BORDER = 1
    BACKGROUND = 2
    RADIAL = 4

    # BORDER STYLE TYPE
    SOLID = "solid"
    DOTTED = "dotted"

    def __init__(self):
        """
        Adds a hover display to a widget.  This makes it so that when
        a users cursor hovers over a widget that widget will show that
        the cursor is over it.

        This will also change the display based off of the current focus
        level.  This is specifically designed for letting users know
        where the current focus point is in the UI.

        Hover
        Hover Select (Mouse pressed after hover)
        Selected No Hover
        Args:
            widget:
            edit_focus (bool): determines if the display property will be turned on/off
            focus (bool): determines if the display property will be turned on/off
            hover (bool): determines if the display property will be turned on/off
            hover_focus (bool): determines if the display property will be turned on/off
            hover_type (hover_display.TYPE): which style sheet should be used
            hover_focus_type (hover_display.TYPE): which style sheet should be used
            focus_type (hover_display.TYPE): which style sheet should be used
            hover_type_flag (dict): of properties for each respective portion
                of the hover type
                {
                    hover:{property:bool, property2:bool},
                    hover_focus:{property:bool, property2:bool},
                    focus:{property:bool}
                }

        Returns (StyleSheet): that has already been formatted
        """
        #self.name = name
        self._hover_style_type = HoverStyleSheet.BORDER
        self._color = repr(iColor["rgba_selected_hover"])
        self._position = None
        self._border_style_type = HoverStyleSheet.SOLID

    def hoverSS(self):
        return self._hoverSS

    def setHoverSS(self, hoverSS):
        """
        Sets the style sheet to be used when hovering.  This style sheet should be only
        the portion embedded within the {}
            ie:
                {type}::hover{hover_focus_properties}{{
                    border: 6px dotted rgba{rgba_invisible};
                    background: {background_select_hover_radial}
                }}
                would only need to include the indented portion

        """
        self._hoverSS = hoverSS

    def hoverFocusSS(self):
        return self._hoverFocusSS

    def setHoverFocusSS(self, hoverFocusSS):
        """
        Sets the style sheet to be used when hovering.  This style sheet should be only
        the portion embedded within the {}
            ie:
                {type}::hover{hover_focus_properties}{{
                    border: 6px dotted rgba{rgba_invisible};
                    background: {background_select_hover_radial}
                }}
                would only need to include the indented portion

        """
        self._hoverFocusSS = hoverFocusSS

    def focusSS(self):
        return self._focusSS

    def setFocusSS(self, focusSS):
        """
        Sets the style sheet to be used when hovering.  This style sheet should be only
        the portion embedded within the {}
            ie:
                {type}::hover{hover_focus_properties}{{
                    border: 6px dotted rgba{rgba_invisible};
                    background: {background_select_hover_radial}
                }}
                would only need to include the indented portion

        """
        self._focusSS = focusSS

    """ PROPERTIES """
    def position(self):
        return self._position

    def setPosition(self, position):
        self._position = position
        self.__createStyleSheets(self.position())

    def color(self):
        return self._color

    def setColor(self, color):
        self._color = repr(color)
        self.__createStyleSheets(self.position())

    def hoverStyleType(self):
        return self._hover_style_type

    def setHoverStyleType(self, hover_style_type):
        self._hover_style_type = hover_style_type
        self.__createStyleSheets(self.position())

    def borderStyleType(self):
        return self._border_style_type

    def setBorderStyleType(self, border_style_type):
        self._border_style_type = border_style_type
        self.__createStyleSheets(self.position())

    """ UTILS """
    def __createStyleSheets(self, position=None):
        """
        Creates the style sheet body for the hover display.

        Args:
            position (attrs.POSITION): How this should be aligned,
                if no value is provided, or set to None, this will
                encompass the entire widget
        """
        style = ""
        if not position:
            style = """
            border-left: 2px {border_style} rgba{color};
            border-right: 2px {border_style} rgba{color};
            border-top: 2px {border_style} rgba{color};
            border-bottom: 2px {border_style} rgba{color};
            """
        # NORTH
        if position == attrs.NORTH:
            style = """
            border-left: 2px {border_style} rgba{color};
            border-right: 2px {border_style} rgba{color};
            border-top: None;
            border-bottom: 2px {border_style} rgba{color};
            """

        # SOUTH
        if position == attrs.SOUTH:
            style = """
            border-left: 2px {border_style} rgba{color};
            border-right: 2px {border_style} rgba{color};
            border-top: 2px {border_style} rgba{color};
            border-bottom: None;
            """
        if position == attrs.EAST:
            style = """
            border-left: 2px {border_style} rgba{color};
            border-right: None
            border-top: 2px {border_style} rgba{color};
            border-bottom: 2px {border_style} rgba{color};
            """
        if position == attrs.WEST:
            style = """
            border-left: None;
            border-right: 2px {border_style} rgba{color};
            border-top: 2px {border_style} rgba{color};
            border-bottom: 2px {border_style} rgba{color};
            """

        if position == attrs.VERTICAL:
            style = """
            border-left: 2px {border_style} rgba{color};
            border-right: 2px {border_style} rgba{color};
            border-top: None;
            border-bottom: None;
            """
        if position == attrs.HORIZONTAL:
            style = """
            border-left: None;
            border-right: None;
            border-top: 2px {border_style} rgba{color};
            border-bottom: 2px {border_style} rgba{color};
            """

        style = style.format(color=self.color(), border_style=self.borderStyleType())

        self.setFocusSS(style)
        self.setHoverSS(style)
        self.setHoverFocusSS(style)

""" CREATE MAIN STYLE SHEET """

def installHoverDisplaySS(
        widget,
        position=None,
        hover_style_type=HoverStyleSheet.BORDER,
        color=iColor["rgba_selected_hover"],
        focus=True,
        hover=True,
        hover_focus=True,
        hover_type_flags={'focus':{}, 'hover_focus':{}, 'hover':{}}):
    """
    Adds a hover display to a widget.  This makes it so that when
    a users cursor hovers over a widget that widget will show that
    the cursor is over it.

    This will also change the display based off of the current focus
    level.  This is specifically designed for letting users know
    where the current focus point is in the UI.

    Hover
    Hover Select (Mouse pressed after hover)
    Selected No Hover
    Args:
        widget (QWidget):
        position (attrs.POSITION): How hover display should be aligned
            attrs ==> NORTH | EAST | SOUTH | WEST | VERTICAL | HORIZONTAL | None
        style_type (HoverStyleSheet.TYPE):
            BORDER | BACKGROUND | RADIAL
        color (RGBA):
        focus (bool): determines if the display property will be turned on/off
        hover (bool): determines if the display property will be turned on/off
        hover_focus (bool): determines if the display property will be turned on/off
        hover_type_flag (dict): of properties for each respective portion
            of the hover type
            {
                hover:{property:bool, property2:bool},
                hover_focus:{property:bool, property2:bool},
                focus:{property:bool}
            }

    Returns (StyleSheet): that has already been formatted

    """

    # create hover object
    hover_object = HoverStyleSheet()
    hover_object.setPosition(position)
    hover_object.setColor(color)
    hover_object.setHoverStyleType(hover_style_type)

    # compile style sheet args
    style_sheet_args = compileSSArgs(widget, hover_type_flags, hover_object)

    style_sheet = "{widget_style_sheet}\n".format(widget_style_sheet=widget.styleSheet())

    # HOVER
    if hover:
        style_sheet += """
            {type}::hover{hover_properties}{{
                {hover_ss}
            }}
            """.format(**style_sheet_args)

    # HOVER FOCUS
    if hover_focus:
        style_sheet += """
            {type}:hover:focus{hover_focus_properties}{{
                {hover_focus_ss}
            }}
            """.format(**style_sheet_args)

    # FOCUS
    if focus:
        style_sheet += """
            {type}:focus{focus_properties}{{
                {focus_ss}
            }}
            """.format(**style_sheet_args)

    widget.setStyleSheet(style_sheet)
