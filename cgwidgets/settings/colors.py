


#
# class iColor(object):
#     """
#     Interface that will hold all of the default color values for the cg widgets library.
#     rgba_outline (rgba): color of the outline for the individual tab labels
#         default color is TansuModelViewWidget.OUTLINE_COLOR
#     rgba_selected (rgba): text color of selected tab
#         default color is TansuModelViewWidget.SELECTED_COLOR
#     rgba_selected_hover (rgba): text color of tab when hovered over
#     rgba_background  (rgba):
#     rgba_background_selected  (rgba):
#
#     """
#
#     """ background"""
#     rgba_background = (32, 32, 32, 255)
#     rgba_background_selected = multiplyRGBAValues(rgba_background)
#
#     """ outline """
#     rgba_outline = (180, 70, 10, 255)
#     rgba_outline_hover = (255, 100, 15, 255)
#
#     """ text """
#
#     rgba_text_color = (192, 192, 192, 255)
#     rgba_text_color_disabled = multiplyRGBAValues(rgba_text_color, mult=0.75)
#     rgba_text_color_hover = multiplyRGBAValues(rgba_text_color)
#
#     """ hover / select"""
#     rgba_selected = (96, 96, 192, 255)
#     rgba_hover = multiplyRGBAValues(rgba_selected)
#
#     """ accept / decline"""
#     rgba_accept = (64, 128, 64, 255)
#     rgba_cancel = (128, 64, 64, 255)
#     rgba_maybe = (64, 64, 128, 255)
#     rgba_error = (192, 0, 0, 255)
#     rgba_accept_hover = multiplyRGBAValues(rgba_accept)
#     rgba_cancel_hover = multiplyRGBAValues(rgba_cancel)
#     rgba_maybe_hover = multiplyRGBAValues(rgba_maybe)
#     rgba_error_hover = multiplyRGBAValues(rgba_error)
#
#     """ default style sheet args"""
#
#     style_sheet_args = {
#         'rgba_background' : repr(rgba_background),
#         'rgba_background_selected' : repr(rgba_background_selected),
#         'rgba_outline' : repr(rgba_outline),
#         'rgba_outline_hover' : repr(rgba_outline_hover),
#         'rgba_selected' : repr(rgba_selected),
#         'rgba_hover' : repr(rgba_hover),
#         'rgba_text_color' : repr(rgba_text_color),
#         'rgba_text_color_hover' : repr(rgba_text_color_hover),
#         'rgba_accept': repr(rgba_accept),
#         'rgba_cancel': repr(rgba_cancel),
#         'rgba_maybe': repr(rgba_maybe),
#         'rgba_error': repr(rgba_error),
#         'rgba_accept_hover': repr(rgba_accept_hover),
#         'rgba_cancel_hover': repr(rgba_cancel_hover),
#         'rgba_maybe_hover': repr(rgba_maybe_hover),
#         'rgba_error_hover': repr(rgba_error_hover),
#         'rgba_text_color_disabled': repr(rgba_text_color_disabled)
#     }
#
#     default_style_sheet = """
#     background-color: rgba{rgba_background_0};
#     color: rgba{rgba_text_color};
#     border: None;
#     """.format(**style_sheet_args)
#
#     @staticmethod
#     def createDefaultStyleSheet(current_instance, updated_args={}):
#         """
#         updated_args (dict): dictionary with updated args
#             to be passed to the default style sheet
#         instance (object): object whose class type should have this
#             style sheet attached onto
#         """
#         style_sheet_args = iColor.style_sheet_args
#         style_sheet_args['type'] = type(current_instance).__name__
#         style_sheet_args.update(updated_args)
#
#         default_style_sheet = """
#         {type}{{
#                 background-color: rgba{rgba_background_0};
#                 color: rgba{rgba_text_color};
#                 border: None;}}
#         """.format(**style_sheet_args)
#         return default_style_sheet
#
#     @staticmethod
#     def multiplyRGBAValues(rgba, mult=1.5):
#         """
#
#         """
#         new_color = []
#         for value in rgba:
#             value *= mult
#             if 255 < value:
#                 value = 255
#             elif value < 0:
#                 value = 0
#             new_color.append(int(value))
#
#         return tuple(new_color)


class Colors(dict):
    def __init__(self):
        """ background"""
        self["rgba_background_0"] = (32, 32, 32, 255)
        self["rgba_background_1"] = Colors.multiplyRGBAValues(self["rgba_background_0"])
        self["rgba_background_2"] = Colors.multiplyRGBAValues(self["rgba_background_1"])
        self["rgba_background_3"] = Colors.multiplyRGBAValues(self["rgba_background_2"])
        self["rgba_background_4"] = Colors.multiplyRGBAValues(self["rgba_background_3"])
        #self["rgba_background_selected"] = Colors.multiplyRGBAValues(self["rgba_background_0"])

        """ outline """
        self["rgba_outline"] = (180, 70, 10, 255)
        self["rgba_outline_hover"] = (255, 100, 15, 255)

        """ text """
        self["rgba_text_color"] = (192, 192, 192, 255)
        self["rgba_text_color_disabled"] = Colors.multiplyRGBAValues(self["rgba_text_color"], golden_ratio_direction=False)
        self["rgba_text_color_hover"] = Colors.multiplyRGBAValues(self["rgba_text_color"])

        """ hover / select"""
        self["rgba_selected"] = (96, 96, 192, 255)
        self["rgba_hover"] = Colors.multiplyRGBAValues(self["rgba_selected"])

        """ accept / decline"""
        self["rgba_accept"] = (64, 128, 64, 255)
        self["rgba_cancel"] = (128, 64, 64, 255)
        self["rgba_maybe"] = (64, 64, 128, 255)
        self["rgba_error"] = (192, 0, 0, 255)
        self["rgba_accept_hover"] = Colors.multiplyRGBAValues(self["rgba_accept"])
        self["rgba_cancel_hover"] = Colors.multiplyRGBAValues(self["rgba_cancel"])
        self["rgba_maybe_hover"] = Colors.multiplyRGBAValues(self["rgba_maybe"])
        self["rgba_error_hover"] = Colors.multiplyRGBAValues(self["rgba_error"])

        """ TANSU """
        self["rgba_tansu_flag"] = (10, 20, 95, 255)
        self["rgba_tansu_handle"] = (10, 95, 20, 255)
        self["rgba_tansu_handle_hover"] = Colors.multiplyRGBAValues(self["rgba_tansu_handle"])

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
        style_sheet_args = iColor.style_sheet_args
        style_sheet_args['type'] = type(current_instance).__name__
        style_sheet_args.update(updated_args)

        default_style_sheet = """
        {type}{{
                background-color: rgba{rgba_background_0};
                color: rgba{rgba_text_color};
                border: None;}}
        """.format(**style_sheet_args)
        return default_style_sheet

    @staticmethod
    def multiplyRGBAValues(rgba, multiplier=None, golden_ratio_direction=True):
        """
        multiply the values be a specific amount.  If

        """
        # setup golden ratio
        if golden_ratio_direction == True:
            mult = 1.618
        else:
            mult = 0.615

        if multiplier:
            mult = multiplier

        new_color = []
        for value in rgba:
            value *= mult
            if 255 < value:
                value = 255
            elif value < 0:
                value = 0
            new_color.append(int(value))

        return tuple(new_color)


iColor = Colors()

