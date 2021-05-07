from PIL import Image

from qtpy.QtWidgets import (QWidget, QFrame, QSizePolicy, QLabel, QVBoxLayout)
from qtpy.QtGui import (QMovie)
from qtpy.QtCore import (Qt, QByteArray, QSize)
from cgwidgets.settings.colors import iColor

class AbstractGIFWidget(QFrame):
    """
    Simple widget to play a gif

    Args:
        gif_file (str): path on disk to gif file to be used

    Attributes:
        file_resolution (int, int): width, height of original file
        resolution (QSize): of current image
    """
    def __init__(self, gif_file, parent=None):
        super(AbstractGIFWidget, self).__init__(parent)

        # create layout
        QVBoxLayout(self)
        self.layout().setAlignment(Qt.AlignCenter)
        self.layout().setContentsMargins(0, 0, 0, 0)

        # setup default attrs
        self._resolution = None

        # setup gif
        self.setGIFFile(gif_file)

    """ UTILS """
    def aspectRatio(self):
        width, height = self.fileResolution()

        aspect_ratio = height / width

        return aspect_ratio

    def fileResolution(self):
        # loading the image
        img = Image.open(self.gifFile())

        # fetching the dimensions
        width, height = img.size

        return width, height

    def resolution(self):
        return self._resolution

    def setResolution(self, width, height=None, maintain_aspect_ratio=None):
        """
        Sets the resolution of the GIF.

        Args:
            width (int):
            height (int):
            maintain_aspect_ratio (bool):
        """
        # aspect ratio enabled
        if maintain_aspect_ratio:
            aspect_ratio = self.aspectRatio()
            res = (width, int(width*aspect_ratio))
        # aspect ratio disabled
        else:
            if width and height:
                res = (width, height)
            elif width:
                aspect_ratio = self.aspectRatio()
                res = (width, int(width*aspect_ratio))

        # set resolution attr
        self._resolution = QSize(*res)

        # set the movie size
        self.movie().setScaledSize(self._resolution)

    """ EVENTS """
    def _event(self):
        "Default mouse press event"
        pass

    def setMousePressEvent(self, event):
        self._event = event

    def mousePressEvent(self, *args, **kwargs):
        self._event()
        return QWidget.mousePressEvent(self, *args, **kwargs)

    def resizeEvent(self, *args, **kwargs):
        # constrain movie widget height to GIF size
        height = self.movie().scaledSize().height()
        self.movieWidget().setFixedHeight(height)
        return QWidget.resizeEvent(self, *args, **kwargs)

    """ PROPERTIES """
    def gifFile(self):
        return self._gif_file

    def setGIFFile(self, gif_file):
        # remove previous gif file
        if hasattr(self, "_movie_widget"):
            self._movie_widget.setParent(None)
            self._movie_widget.deleteLater()

        # setup attr
        self._gif_file = gif_file

        # create new movie widget
        self._movie_widget = QLabel()
        self.layout().addWidget(self._movie_widget)

        self._movie = QMovie(gif_file, QByteArray(), self._movie_widget)
        self.setResolution(*self.fileResolution())

        self._movie_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # start movie
        self._movie.setCacheMode(QMovie.CacheAll)
        self._movie_widget.setMovie(self._movie)
        self._movie.start()
        self._movie.loopCount()

    def movie(self):
        return self._movie

    def movieWidget(self):
        return self._movie_widget


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication
    from cgwidgets.utils import centerWidgetOnCursor
    from cgwidgets.settings.hover_display import installHoverDisplaySS
    from cgwidgets.settings.icons import icons

    app = QApplication(sys.argv)

    gif_file = icons["ACCEPT_GIF"]
    widget = AbstractGIFWidget(gif_file)
    installHoverDisplaySS(widget)

    widget.show()
    centerWidgetOnCursor(widget)
    widget.setResolution(50, maintain_aspect_ratio=True)

    sys.exit(app.exec_())