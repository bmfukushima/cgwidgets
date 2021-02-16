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

from .colors import iColor
from .stylesheets import convertDictToCSSFlags, background_radial

""" UTILS """
def compileSSArgs(widget, hover_type_flags, hover_type, focus_type, hover_focus_type):
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
            rgba_background=iColor["rgba_background"],
            rgba_background_2=iColor["rgba_selected_background"]),
        "background_cancel_radial":background_radial.format(
            rgba_background=iColor["rgba_background"],
            rgba_background_2=iColor["rgba_cancel"]),
        "background_accept_radial":background_radial.format(
            rgba_background=iColor["rgba_background"],
            rgba_background_2=iColor["rgba_accept"]),
        "background_select_hover_radial":background_radial.format(
            rgba_background=iColor["rgba_background"],
            rgba_background_2=iColor["rgba_selected_hover"])
    })

    # add widget SS
    style_sheet_args.update({
        'type': type(widget).__name__,
        'hover_ss': hover_type.hoverSS().format(**style_sheet_args),
        'focus_ss': focus_type.focusSS().format(**style_sheet_args),
        'hover_focus_ss': hover_focus_type.focusSS().format(**style_sheet_args)
    })

    return style_sheet_args

class HoverStyleSheet(object):
    def __init__(self, name):
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
        self.name = name

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

""" CREATE STYLE SHEETS """
TEST = HoverStyleSheet("TEST")
TEST.setFocusSS("""background: rgba(255,0,0,255);""")
TEST.setHoverSS("""background: rgba(0,255,0,255);""")
TEST.setHoverFocusSS("""background: rgba(0,0,255,255);""")

BORDER_00 = HoverStyleSheet("BORDER_00")
BORDER_00.setFocusSS("""border: 6px dotted rgba{rgba_invisible};""")
BORDER_00.setHoverSS("""border: 6px dotted rgba{rgba_background};""")
BORDER_00.setHoverFocusSS("""border: 6px dotted rgba{rgba_invisible};""")

BACKGROUND_00 = HoverStyleSheet("BACKGROUND_00")
BACKGROUND_00.setFocusSS("""
    border: 6px dotted rgba{rgba_invisible};
    background: {background_hover_radial};""")
BACKGROUND_00.setHoverSS("""
    border: 6px dotted rgba{rgba_invisible};
    background: {background_select_hover_radial};""")
BACKGROUND_00.setHoverFocusSS("""
    border: 6px dotted rgba{rgba_invisible};
    background: {background_hover_radial};""")


""" CREATE MAIN STYLE SHEET """
def installHoverDisplaySS(
        widget,
        hover_type=TEST,
        focus_type=TEST,
        hover_focus_type=TEST,
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

    style_sheet_args = compileSSArgs(widget, hover_type_flags, hover_type, focus_type, hover_focus_type)

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
