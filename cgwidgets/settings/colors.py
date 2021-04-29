"""
TODO
    Color Pallette...
        Green ( GO )
        Yellow ( SLOW )
        Red ( STOP )
        blue ( MOVEABLE THINGY )
        normals blue ( SELECTION )
    Gray's
        UI dark theme
    rgba_outline / shoji
        These will need to be updated

"""

from qtpy.QtGui import QColor

from cgwidgets.utils import attrs


class Colors(dict):
    def __init__(self):

        """ COLOR GENERATOR """
        # CONSTANT
        self["rgba_black"] = (0, 0, 0, 255)
        self["rgba_white"] = (255, 255, 255, 255)
        self["rgba_invisible"] = (0, 0, 0, 0)

        # COLOR GRADIENTS
        num_colors = 8
        start_color = 10
        # pure blood
        createColorRange("rgba_gray", (start_color, start_color, start_color, 255), self, num_colors, desaturate=False)
        createColorRange("rgba_blue", (0, 0, start_color, 255), self, num_colors)
        createColorRange("rgba_green", (0, start_color, 0, 255), self, num_colors)
        createColorRange("rgba_red", (start_color, 0, 0, 255), self, num_colors)

        # mud blood
        createColorRange("rgba_yellow", (start_color, start_color, start_color*0.5, 255), self, num_colors, desaturate=False)
        createColorRange("rgba_cyan", (start_color * 0.5, start_color, start_color, 255), self, num_colors, desaturate=False)
        createColorRange("rgba_magenta", (start_color, start_color * 0.5, start_color * 0.5, 255), self, num_colors, desaturate=False)
        """ COLOR REFERENCES"""
        """ background """
        self["rgba_background_00"] = self["rgba_gray_2"]
        self["rgba_background_01"] = self["rgba_gray_3"]

        """ outline """
        self["rgba_outline"] = self["rgba_blue_6"]
        self["rgba_outline_hover"] = self["rgba_blue_7"]

        """ text """
        self["rgba_text"] = self["rgba_gray_7"]
        self["rgba_text_disabled"] = Colors.multiplyRGBAValues(self["rgba_text"], golden_ratio=False, alpha=255)
        self["rgba_text_hover"] = self["rgba_cyan_7"]

        """ hover / select"""
        self["rgba_selected_background"] = self["rgba_cyan_5"]
        self["rgba_selected"] = self["rgba_cyan_6"]
        self["rgba_selected_hover"] = self["rgba_cyan_5"]

        """ accept / decline"""
        self["rgba_accept"] = self["rgba_green_desat_6"]
        self["rgba_cancel"] = self["rgba_red_desat_6"]
        self["rgba_maybe"] =  self["rgba_yellow_5"]
        self["rgba_error"] =  self["rgba_red_7"]
        self["rgba_accept_hover"] = Colors.multiplyRGBAValues(self["rgba_accept"], golden_ratio=True)
        self["rgba_cancel_hover"] = Colors.multiplyRGBAValues(self["rgba_cancel"], golden_ratio=True)
        self["rgba_maybe_hover"] = Colors.multiplyRGBAValues(self["rgba_maybe"], golden_ratio=True)
        self["rgba_error_hover"] = Colors.multiplyRGBAValues(self["rgba_error"], golden_ratio=True)

        self.style_sheet_args = self.createStyleSheetArgs()

    def createStyleSheetArgs(self):
        args = {}
        for color in list(self.keys()):
            args[color] = repr(self[color])
        return args

    @staticmethod
    def createDefaultStyleSheet(current_instance, updated_args={}):
        """
        updated_args (dict): dictionary with updated args
            to be passed to the default style sheet
        instance (object): object whose class type should have this
            style sheet attached onto
        """
        args = {
            'type': type(current_instance).__name__,
            'rgba_background': iColor['rgba_background_00'],
            'rgba_text': iColor['rgba_text'],
            'additional_args': ''
        }

        args.update(updated_args)
        default_style_sheet = """
        {type}{{
                background-color: rgba{rgba_background};
                color: rgba{rgba_text};
                border: None;}}
        {additional_args}
        """.format(**args)
        return default_style_sheet

    @staticmethod
    def multiplyRGBAValues(rgba, multiplier=1, golden_ratio=None, alpha=None):
        """
        multiply the values be a specific amount.

        Args:
            rgba (tuple rgba 0-255): values to be modified
            multiplier (float) amount to multiply by
            golden_ratio (bool): Determines if this should be increased/decreased
                by the golden ratio.  If set to None, it will multiply by 1
            alpha (int): new alpha, if not provided this will return whatever the maths
                returns.  This is most notably useful when decreasing values, to
                keep the color opaque.
        """

        # setup golden ratio
        if golden_ratio == True:
            golden_value = 1.618
        elif golden_ratio == False:
            golden_value = 0.615
        else:
            golden_value = 1

        # multiply values
        new_color = []
        for value in rgba:
            value *= golden_value * multiplier
            if 255 < value:
                value = 255
            elif value < 0:
                value = 0
            new_color.append(int(value))

        # override alpha
        if alpha:
            new_color[3] = alpha

        return tuple(new_color)


def getHSVRGBAFloatFromColor(color):
    new_color_args = {
        "hue": color.hueF(),
        "value": color.valueF(),
        "saturation": color.saturationF(),
        "red": color.redF(),
        "green": color.greenF(),
        "blue": color.blueF(),
        "alpha": color.alphaF()
    }

    return new_color_args


def updateColorFromArgValue(orig_color, arg, value):
    """
    Returns a new qcolor based off of the color arg/value combo provided.
    This will only update the one color arg of the original color, and return a new
    instance of that original color.

    Args
        orig_color (QColor): The original color whose value you want to adjust...
        arg (attrs.COLOR_ARG):
        value (float):

    Returns (QColor)
    """

    new_color = QColor(*orig_color.getRgb())
    selection_type = arg
    # saturation
    if selection_type == attrs.SATURATION:
        hue = new_color.hueF()
        sat = value
        value = new_color.valueF()
        new_color.setHsvF(hue, sat, value)
    # hue
    elif selection_type == attrs.HUE:
        hue = value
        sat = new_color.saturationF()
        value = new_color.valueF()
        new_color.setHsvF(hue, sat, value)
    # value
    elif selection_type == attrs.VALUE:
        # get HSV values
        hue = new_color.hueF()
        sat = new_color.saturationF()
        value = value
        new_color.setHsvF(hue, sat, value)
    # red
    elif selection_type == attrs.RED:
        red = value
        new_color.setRedF(red)
    # green
    elif selection_type == attrs.GREEN:
        green = value
        new_color.setGreenF(green)
    # blue
    elif selection_type == attrs.BLUE:
        blue = value
        new_color.setBlueF(blue)

    # set color from an arg value
    return new_color


def createColorRange(name, color, colors_dict, num_values=8, desaturate=True):
    """
    Creates a range of colors from the original color provided.

    Args:
        name (string):
        color (tuple(RGBA)):
        colors_dict (dict): main container storing colors
        num_values (int): number of values to create

    Returns:

    """
    colors_dict["{name}_0".format(name=name)] = color

    for x in range(1, num_values):
        # create color
        colors_dict["{name}_{x}".format(x=x, name=name)] = Colors.multiplyRGBAValues(
            colors_dict["{name}_{y}".format(name=name, y=x - 1)], golden_ratio=True)

        # desaturated color
        if desaturate:
            colors_dict["{name}_desat_{x}".format(x=x, name=name)] = desaturateColor(colors_dict["{name}_{x}".format(x=x, name=name)])
    return colors_dict


def desaturateColor(color, desaturation_amount=0.5):
    """
    Takes a color, and returns a color that is desaturated by the amount provided.
    Args:
        color (RGBA): tuple of RGBA 255 values
        desaturation_amount (float): amount to desaturate color by

    Returns (RGBA):

    """
    desaturate_color = []
    initial_value = max(color[:3])
    for c in color:
        if c < initial_value:
            new_value = int(c + (initial_value * desaturation_amount))
            desaturate_color.append(new_value)
        else:
            desaturate_color.append(c)
    return tuple(desaturate_color)


iColor = Colors()
