from cgwidgets.widgets import AbstractGIFWidget


class GIFWidget(AbstractGIFWidget):
    """
    Simple widget to play a gif

    Args:
        gif_file (str): path on disk to gif file to be used

    Attributes:
        file_resolution (int, int): width, height of original file
        resolution (QSize): of current image
    """
    def __init__(self, gif_file, parent=None):
        super(GIFWidget, self).__init__(gif_file, parent)