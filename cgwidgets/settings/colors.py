"""
TODO
    Color Pallette...
        Green ( GO )
        Yellow ( SLOW )
        Red ( STOP )
        blue
        normals blue
    Gray's
        UI dark theme
    rgba_outline / tansu
        These will need to be updated

"""

from qtpy.QtGui import QColor

from cgwidgets.utils import attrs


class Colors(dict):
    def __init__(self):
        """ background"""
        self["rgba_invisible"] = (0, 0, 0, 0)
        self["rgba_gray_0"] = (32, 32, 32, 255)
        self["rgba_gray_1"] = Colors.multiplyRGBAValues(self["rgba_gray_0"], golden_ratio=True)
        self["rgba_gray_2"] = Colors.multiplyRGBAValues(self["rgba_gray_1"], golden_ratio=True)
        self["rgba_gray_3"] = Colors.multiplyRGBAValues(self["rgba_gray_2"], golden_ratio=True)
        self["rgba_gray_4"] = Colors.multiplyRGBAValues(self["rgba_gray_3"], golden_ratio=True)

        """ blue """
        self["rgba_blue_0"] = (0, 0, 32, 255)
        self["rgba_blue_1"] = Colors.multiplyRGBAValues(self["rgba_blue_0"], golden_ratio=True)
        self["rgba_blue_2"] = Colors.multiplyRGBAValues(self["rgba_blue_1"], golden_ratio=True)
        self["rgba_blue_3"] = Colors.multiplyRGBAValues(self["rgba_blue_2"], golden_ratio=True)
        self["rgba_blue_4"] = Colors.multiplyRGBAValues(self["rgba_blue_3"], golden_ratio=True)

        """ green """
        self["rgba_green_0"] = (0, 32, 0, 255)
        self["rgba_green_1"] = Colors.multiplyRGBAValues(self["rgba_green_0"], golden_ratio=True)
        self["rgba_green_2"] = Colors.multiplyRGBAValues(self["rgba_green_1"], golden_ratio=True)
        self["rgba_green_3"] = Colors.multiplyRGBAValues(self["rgba_green_2"], golden_ratio=True)
        self["rgba_green_4"] = Colors.multiplyRGBAValues(self["rgba_green_3"], golden_ratio=True)
        #self["rgba_gray_selected"] = Colors.multiplyRGBAValues(self["rgba_gray_0"])

        """ outline """
        # self["rgba_outline"] = (180, 70, 10, 255)
        # self["rgba_outline_hover"] = (255, 100, 15, 255)
        self["rgba_outline"] = self["rgba_green_3"]
        self["rgba_outline_hover"] = self["rgba_green_4"]

        """ text """
        self["rgba_text"] = (192, 192, 192, 255)
        self["rgba_text_disabled"] = Colors.multiplyRGBAValues(self["rgba_text"], golden_ratio=False, alpha=255)
        self["rgba_text_hover"] = Colors.multiplyRGBAValues(self["rgba_text"], golden_ratio=True)

        """ hover / select"""
        self["rgba_selected"] = (96, 96, 192, 255)
        self["rgba_hover"] = Colors.multiplyRGBAValues(self["rgba_selected"], golden_ratio=True)

        """ accept / decline"""
        self["rgba_accept"] = (64, 128, 64, 255)
        self["rgba_cancel"] = (128, 64, 64, 255)
        self["rgba_maybe"] = (64, 64, 128, 255)
        self["rgba_error"] = (192, 0, 0, 255)
        self["rgba_accept_hover"] = Colors.multiplyRGBAValues(self["rgba_accept"], golden_ratio=True)
        self["rgba_cancel_hover"] = Colors.multiplyRGBAValues(self["rgba_cancel"], golden_ratio=True)
        self["rgba_maybe_hover"] = Colors.multiplyRGBAValues(self["rgba_maybe"], golden_ratio=True)
        self["rgba_error_hover"] = Colors.multiplyRGBAValues(self["rgba_error"], golden_ratio=True)

        """ TANSU """
        self["rgba_tansu_flag"] = (10, 20, 95, 255)
        self["rgba_tansu_handle"] = (10, 95, 20, 255)
        self["rgba_tansu_handle_hover"] = Colors.multiplyRGBAValues(self["rgba_tansu_handle"], golden_ratio=True)

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
            'rgba_background': iColor['rgba_gray_0'],
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


iColor = Colors()
