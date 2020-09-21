#from cgwidgets.utils import multiplyRGBAValues
def multiplyRGBAValues(rgba, mult=1.5):
    """

    """
    new_color = []
    for value in rgba:
        value *= mult
        if 255 < value:
            value = 255
        elif value < 0:
            value = 0
        new_color.append(int(value))

    return tuple(new_color)

# NOT IN USE
def getTopBorderStyleSheet(border_color, border_width):
    """
    Returns a style sheet for adding the top border of something to do something.
    This is mainly used in input widgets with headings above them.
    """
    #    padding-top: 5px;
    # margin-top: 10px
    style_sheet ="""
    AbstractInputWidget{{border: {border_width}px solid rgba{border_color};
    border-right: None;
    border-left: None;
    border-bottom: None;
    background-color: rgba(0,0,0,0);
    }}
    """.format(
        border_color=border_color,
        border_width=border_width
    )
    return style_sheet

""" TANSU """
RGBA_TANSU_FLAG = (10, 20, 95, 255)
RGBA_TANSU_HANDLE = (10, 95, 20, 255)
RGBA_TANSU_HANDLE_HOVER = multiplyRGBAValues(RGBA_TANSU_HANDLE)


class iColor(object):
    """
    Interface that will hold all of the default color values for the cg widgets library.
    rgba_outline (rgba): color of the outline for the individual tab labels
        default color is TansuModelViewWidget.OUTLINE_COLOR
    rgba_selected (rgba): text color of selected tab
        default color is TansuModelViewWidget.SELECTED_COLOR
    rgba_selected_hover (rgba): text color of tab when hovered over
    rgba_background  (rgba):
    rgba_background_selected  (rgba):

    """

    """ background"""
    rgba_background = (32, 32, 32, 255)
    rgba_background_selected = multiplyRGBAValues(rgba_background)

    """ outline """
    rgba_outline = (180, 70, 10, 255)
    rgba_outline_hover = (255, 100, 15, 255)

    """ text """
    rgba_text_color = (128, 128, 128, 255)
    rgba_text_color_hover = multiplyRGBAValues(rgba_text_color)

    """ hover / select"""
    rgba_selected = (96, 96, 192, 255)
    rgba_hover = multiplyRGBAValues(rgba_selected)

    """ accept / decline"""
    rgba_accept = (64, 128, 64, 255)
    rgba_cancel = (128, 64, 64, 255)
    rgba_maybe = (64, 64, 128, 255)
    rgba_error = (192, 0, 0, 255)
    rgba_accept_hover = multiplyRGBAValues(rgba_accept)
    rgba_cancel_hover = multiplyRGBAValues(rgba_cancel)
    rgba_maybe_hover = multiplyRGBAValues(rgba_maybe)
    rgba_error_hover = multiplyRGBAValues(rgba_error)

    """ default style sheet args"""

    style_sheet_args = {
        'rgba_background' : repr(rgba_background),
        'rgba_background_selected' : repr(rgba_background_selected),
        'rgba_outline' : repr(rgba_outline),
        'rgba_outline_hover' : repr(rgba_outline_hover),
        'rgba_selected' : repr(rgba_selected),
        'rgba_hover' : repr(rgba_hover),
        'rgba_text_color' : repr(rgba_text_color),
        'rgba_text_color_hover' : repr(rgba_text_color_hover),
        'rgba_accept': repr(rgba_accept),
        'rgba_cancel': repr(rgba_cancel),
        'rgba_maybe': repr(rgba_maybe),
        'rgba_error': repr(rgba_error),
        'rgba_accept_hover': repr(rgba_accept_hover),
        'rgba_cancel_hover': repr(rgba_cancel_hover),
        'rgba_maybe_hover': repr(rgba_maybe_hover),
        'rgba_error_hover': repr(rgba_error_hover),
    }

    default_style_sheet = """
    background-color: rgba{rgba_background};
    color: rgba{rgba_text_color};
    border: None;
    """.format(**style_sheet_args)

    def createDefaultStyleSheet(updated_style_sheet_args):
        style_sheet_args = iColor.style_sheet_args
        style_sheet_args.update(updated_style_sheet_args)

        default_style_sheet = """
            background-color: rgba{rgba_background};
            color: rgba{rgba_text_color};
            border: None;
        """.format(**style_sheet_args)
        return default_style_sheet

    def multiplyRGBAValues(rgba, mult=1.5):
        """

        """
        new_color = []
        for value in rgba:
            value *= mult
            if 255 < value:
                value = 255
            elif value < 0:
                value = 0
            new_color.append(int(value))

        return tuple(new_color)

