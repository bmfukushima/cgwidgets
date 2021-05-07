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
import re
import copy

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
    style_sheet_args.update({
        'type': type(widget).__name__,
        'hover_ss': hover_object.hoverSS().format(**style_sheet_args),
        'focus_ss': hover_object.focusSS().format(**style_sheet_args),
        'hover_focus_ss': hover_object.focusSS().format(**style_sheet_args),
        'default_ss': hover_object.defaultSS().format(**style_sheet_args)
    })

    return style_sheet_args


class BorderStyleSheet(object):
    """
    Arbitray object for creating Border Style Sheets.

    Attributes:
        color (string): rgba 255
            (255, 255, 255, 255)
        style (BorderStyleSheet.STYLE):
            SOLID | DOTTED
        walls (tuple): of attr.DIRECTION
            (attrs.NORTH, attrs.SOUTH, attrs.EAST, attrs.WEST)
    """
    # BORDER STYLE TYPE
    SOLID = "solid"
    DOTTED = "dotted"

    def __init__(self):
        self._style = BorderStyleSheet.SOLID
        self._color = iColor["rgba_selected_hover"]
        self._walls = (attrs.NORTH, attrs.SOUTH, attrs.EAST, attrs.WEST)

    def walls(self):
        return self._walls

    def setWalls(self, walls):
        self._walls = walls

    def color(self):
        return self._color

    def setColor(self, color):
        self._color = color

    def style(self):
        return self._style

    def setStyle(self, style):
        self._style = style

    @staticmethod
    def remapDirectionToStyleSheet(direction):
        """
        Remaps the direction from cgwidgets.attrs.POSITION to stylesheet
        Args:
            direction (attrs.POSITION):

        Returns (str): attrs.DIRECTION of mapped value that will work in
            a CSS StyleSheet
        """
        if direction == attrs.NORTH:
            return "top"
        if direction == attrs.SOUTH:
            return "bottom"
        if direction == attrs.EAST:
            return "right"
        if direction == attrs.WEST:
            return "left"

    def styleSheet(self):
        """
        Creates a style sheet body to create the border walls

        Returns (string): Style Sheet
        """
        # create default attrs
        all_walls = ['top', 'bottom', 'right', 'left']
        style_sheet = ""

        for wall in self.walls():
            side = BorderStyleSheet.remapDirectionToStyleSheet(wall)
            style_sheet += 'border-{side}: 2px {style} rgba{color};\n'.format(
                side=side, style=self.style(), color=self.color())

            all_walls.remove(side)

        return style_sheet


class HoverStyleSheet(object):
    """
    Arbitrary helper object containing all properties needed by the StyleSheet to setup Hover Displays.

    Attributes:
        position (attrs.POSITION): the cardinal direction
        color (RGBA): 255 RGBA color to be displayed
        hover_style_type (HoverStyleSheet.HOVER_STYLE_TYPE): what type of hover display should be shown
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
        self._hover_color = repr(iColor["rgba_selected_hover"])
        self._focus_color = repr(iColor["rgba_selected_hover"])
        self._position = None
        self._border_hover_style_type = BorderStyleSheet.DOTTED
        self._border_focus_style_type = BorderStyleSheet.SOLID

    """ STYLE SHEETS"""
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

    def defaultSS(self):
        return self._defaultSS

    def setDefaultSS(self, defaultSS):
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
        self._defaultSS = defaultSS

    """ PROPERTIES """
    def position(self):
        return self._position

    def setPosition(self, position):
        self._position = position
        self.__createStyleSheets()

    def focusColor(self):
        return self._focus_color

    def setFocusColor(self, _focus_color):
        self._focus_color = repr(_focus_color)
        self.__createStyleSheets()

    def hoverColor(self):
        return self._hover_color

    def setHoverColor(self, _hover_color):
        self._hover_color = repr(_hover_color)
        self.__createStyleSheets()

    def hoverStyleType(self):
        return self._hover_style_type

    def setHoverStyleType(self, hover_style_type):
        self._hover_style_type = hover_style_type
        if hover_style_type == HoverStyleSheet.BORDER:
            self.setBorderWalls((attrs.NORTH, attrs.SOUTH, attrs.EAST, attrs.WEST))
        self.__createStyleSheets()

    """ BORDER """
    def borderWalls(self):
        return self._border_walls

    def setBorderWalls(self, border_walls):
        self._border_walls = border_walls
        self.__createStyleSheets()

    def borderHoverStyleType(self):
        return self._border_hover_style_type

    def setBorderHoverStyleType(self, _border_hover_style_type):
        self._border_hover_style_type = _border_hover_style_type
        self.__createStyleSheets()

    def borderFocusStyleType(self):
        return self._border_focus_style_type

    def setBorderFocusStyleType(self, _border_focus_style_type):
        self._border_focus_style_type = _border_focus_style_type
        self.__createStyleSheets()

    """ UTILS """
    def __createStyleSheets(self):
        """
        Creates the style sheet body for the hover display.

        Args:
            walls (tuple): of attrs.POSITIONS that will have the border
                displayed around them.  Valid options are:
                    (attrs.NORTH, attrs.SOUTH, attrs.EAST, attrs.WEST)
                Note: This option is only valid when the HoverStyleSheet.hoverStyleType
                    is set to HoverStyleSheet.BORDER
        """
        if self.hoverStyleType() == HoverStyleSheet.BORDER:
            # create border object
            style_sheet_object = BorderStyleSheet()
            style_sheet_object.setWalls(self.borderWalls())

            # setup border
            style_sheet_object.setColor(repr(iColor["rgba_invisible"]))

            # create a default style sheet if None is provided
            self.setDefaultSS(style_sheet_object.styleSheet())

            # setup hover
            hover_style_sheet = copy.deepcopy(style_sheet_object)
            hover_style_sheet.setColor(self.hoverColor())
            hover_style_sheet.setStyle(self.borderHoverStyleType())

            # setup focus
            focus_style_sheet = copy.deepcopy(style_sheet_object)
            focus_style_sheet.setStyle(self.borderFocusStyleType())
            focus_style_sheet.setColor(self.focusColor())

            # setup focus/hover/hover focus
            self.setFocusSS(focus_style_sheet.styleSheet())
            self.setHoverFocusSS(focus_style_sheet.styleSheet())
            self.setHoverSS(hover_style_sheet.styleSheet())


""" CREATE MAIN STYLE SHEET """
def installHoverDisplaySS(
        widget,
        name="",
        border_walls=(attrs.NORTH, attrs.SOUTH, attrs.EAST, attrs.WEST),
        border_focus_style_type=BorderStyleSheet.SOLID,
        border_hover_style_type=BorderStyleSheet.DOTTED,
        default_ss=None,
        hover_style_type=HoverStyleSheet.BORDER,
        hover_color=iColor["rgba_selected_hover"],
        focus_color=iColor["rgba_selected"],
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
        border_walls (list): of attrs.DIRECTION that will have the border shown on
            attrs.NORTH | attrs.SOUTH | attrs.EAST | attrs.WEST
        border_focus_style_type (BorderStyleSheet.STYLE): What style the border of the FOCUSED widgets is
            DOTTED | SOLID
        border_hover_style_type (BorderStyleSheet.STYLE): What style the border of the HOVERED widgets is
            DOTTED | SOLID
        default_ss (StyleSheet): default style sheet that will be added after the widgets initial stylesheet.
            This allows for you to override the default border that is displayed... finally
        name (str): unique name to cull
        hover_style_type (HoverStyleSheet.TYPE): How to display the hover style type.
            BORDER | BACKGROUND | RADIAL
            Note:
                Only BORDER works right now
        focus_color (RGBA): color displayed when widget is FOCUSED
            (255, 255, 255, 255)
        hover_color (RGBA): colored displayed when cursor HOVERS over widget
            (255, 255, 255, 255)
        focus (bool): determines if the display property will be turned on/off
        hover (bool): determines if the display property will be turned on/off
        hover_focus (bool): determines if the display property will be turned on/off
        hover_type_flags (dict): These flags will be installed on the respective portion
            of the style sheet hover type.
            {
                hover:{property:bool, property2:bool},
                hover_focus:{property:bool, property2:bool},
                focus:{property:bool}
            }
            Note:
                This is to allow extra properties to be added and called to dynamically control the
                hover display later

    Returns (StyleSheet): that has already been formatted

    """

    # create hover object
    hover_object = HoverStyleSheet()
    hover_object.setHoverStyleType(hover_style_type)
    hover_object.setHoverColor(hover_color)
    hover_object.setFocusColor(focus_color)

    # setup border
    if hover_style_type == HoverStyleSheet.BORDER:
        hover_object.setBorderWalls(border_walls)
        hover_object.setBorderHoverStyleType(border_hover_style_type)
        hover_object.setBorderFocusStyleType(border_focus_style_type)

    # setup default SS
    if default_ss:
        hover_object.setDefaultSS(default_ss)

    # compile style sheet args
    style_sheet_args = compileSSArgs(widget, hover_type_flags, hover_object)

    style_sheet = "{widget_style_sheet}".format(widget_style_sheet=widget.styleSheet())

    # remove previous hover display
    style_sheet = removeHoverDisplay(style_sheet, name)
    # START
    style_sheet += "\n/* << HOVER {name} DISPLAY START >> */ \n".format(name=name)

    # add border padding
    style_sheet += """
/* Hover Display Border Padding */
{type}{{
    {default_ss}
}}
    """.format(**style_sheet_args)
    # HOVER
    if hover:
        style_sheet += """
/* Hover Display Hover */
{type}::hover{hover_properties}{{
    {hover_ss}
}}
            """.format(**style_sheet_args)

    # HOVER FOCUS
    if hover_focus:
        style_sheet += """
/* Hover Display Hover Focus */
{type}:hover:focus{hover_focus_properties}{{
    {hover_focus_ss}
}}
""".format(**style_sheet_args)

    # FOCUS
    if focus:
        style_sheet += """
/* Hover Display Hover */
{type}:focus{focus_properties}{{
    {focus_ss}
}}
""".format(**style_sheet_args)

    # END
    style_sheet += "\n/* << HOVER {name} DISPLAY END >> */ \n".format(name=name)

    # print ('==============================')
    # print(style_sheet)
    widget.setStyleSheet(style_sheet)

def removeHoverDisplay(style_sheet, name):
    """
    Removes the hover display from a widget

    Args:
        style_sheet (StyleSheet): style sheet to have hover display removed from

    Returns (StyleSheet):
    """
    #style_sheet = widget.styleSheet()

    new_style_sheet = re.sub(
        "(\n/\* << HOVER {name} DISPLAY START >> \*/ \n)([^\$]+)(\n/\* << HOVER {name} DISPLAY END >> \*/ \n)".format(name=name),
        "",
        style_sheet)
    # print ('===================')
    # print(new_style_sheet)
    # print ('===================')
    return new_style_sheet


