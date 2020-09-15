from cgwidgets.utils import multiplyRGBAValues

################################
#########    COLORS    ###########
################################
""" ACCEPTS / DECLINE / MAYBE"""
RGBA_ACCEPT = (64, 128, 64, 255)
RGBA_CANCEL = (128, 64, 64, 255)
RGBA_MAYBE = (64, 64, 128, 255)
RGBA_ERROR = (192, 0, 0, 255)

RGBA_ACCEPT_HOVER = multiplyRGBAValues(RGBA_ACCEPT)
RGBA_CANCEL_HOVER = multiplyRGBAValues(RGBA_CANCEL)
RGBA_MAYBE_HOVER = multiplyRGBAValues(RGBA_MAYBE)
RGBA_ERROR_HOVER = multiplyRGBAValues(RGBA_ERROR)

""" TANSU """
RGBA_TANSU_HANDLE = (10, 95, 20, 255)
RGBA_TANSU_HANDLE_HOVER = multiplyRGBAValues(RGBA_TANSU_HANDLE)

""" SELECTED """
RGBA_SELECTED = (96, 96, 192, 255)
RGBA_SELECTED_HOVER = multiplyRGBAValues(RGBA_SELECTED)

""" OUTLINE """
RGBA_OUTLINE = (255, 100, 15, 255)


