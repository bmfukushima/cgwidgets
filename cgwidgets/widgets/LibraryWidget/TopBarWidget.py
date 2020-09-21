import math

from qtpy.QtWidgets import *
from qtpy.QtCore import *

from .__utils__ import iUtils
from cgwidgets import utils as gUtils

class TopBarMainWidget(QWidget):
    """
    Has all of the user input settings for manipulating/adjusting
    how the Library is displayed to them

    @publish_toggle <QPushButton>
        Toggles if the GUI is in Get or Set mode

    """
    def __init__(self, parent=None):
        super(TopBarMainWidget, self).__init__(parent)
        self.main_layout = QHBoxLayout()
        #self.main_layout.setAlignment(Qt.AlignBottom)
        self.setLayout(self.main_layout)
        self.mode_container = ModeContainer(self)

        self.size_button_container = ImageSizeButtonContainer(self)

        self.main_layout.addWidget(self.size_button_container)
        self.main_layout.addWidget(self.mode_container)

    """ USER wtf """


class TopBarWidgetContainer(QGroupBox):
    def __init__(self, parent=None, title='title', layout='h'):
        super(TopBarWidgetContainer, self).__init__(parent)
        # set title
        self.setTitle(title)

        # set up stylesheet
        self.setStyleSheet(iUtils.getSetting('TOP_BAR_CONTAINER_SS'))

        # set up layout
        if layout.startswith('h'):
            self.main_layout = QHBoxLayout()
        elif layout.startswith('v'):
            self.main_layout = QVBoxLayout()

        self.setLayout(self.main_layout)
        # self.main_layout.setContentsMargins(10, 10, 10, 10)


class ViewModeDropDown(QComboBox):
    def __init__(self, parent=None):
        super(ViewModeDropDown, self).__init__(parent)
        self.addItems(['List', 'Detailed', 'Thumbnail', 'Publish'])
        self.currentIndexChanged.connect(self.indexChanged)

    def indexChanged(self):
        mode = self.currentText()
        main_widget = gUtils.getMainWidget(self, 'Library')
        model = iUtils.getModel(self)
        if mode == 'Publish':
            self.switchToPublishView(main_widget)
        elif mode == 'Thumbnail':
            self.switchToThumbnailView(main_widget, model)
        elif mode == 'Detailed':
            self.switchToDetailedView(main_widget, model)
        elif mode == 'List':
            self.switchToListView(main_widget, model)

    def switchToThumbnailView(self, main_widget, model):
        main_widget.search_bar.show()
        for item in main_widget.thumbnail_view.widget_list:
            if item in model.metadata['selected']:
                item.setSelected()
        main_widget.working_area_layout.setCurrentIndex(0)

    def switchToDetailedView(self, main_widget, model):
        main_widget.search_bar.show()
        main_widget.working_area_layout.setCurrentIndex(1)

    def switchToListView(self, main_widget, model):
        main_widget.search_bar.show()
        main_widget.working_area_layout.setCurrentIndex(2)

    def switchToPublishView(self, main_widget):
        main_widget.search_bar.hide()
        main_widget.working_area_layout.setCurrentIndex(3)


class ModeContainer(TopBarWidgetContainer):
    def __init__(self, parent=None):
        super(ModeContainer, self).__init__(parent, title='Mode', layout='h')
        #self.mode_container = TopBarWidgetContainer(self, title='Mode', layout='h')
        self.mode_menu = ViewModeDropDown(self)
        self.main_layout.layout().addWidget(self.mode_menu)


class ImageSizeButtonContainer(TopBarWidgetContainer):
    """
    Container holding all of the squares to change the
    size that the image is displayed to the user
    """
    def __init__(self, parent=None):
        super(ImageSizeButtonContainer, self).__init__(parent, title='Display Size', layout='h')
        # attrs
        self.spacing = 10
        self.thumbnail_view_sizes = iUtils.getSetting('IMAGE_SIZES')
        self.thumbnail_view_buttons = {}

        # setup spacing
        self.main_layout.setAlignment(Qt.AlignBottom)
        self.main_layout.setContentsMargins(self.spacing, self.spacing, self.spacing, self.spacing)
        self.main_layout.setSpacing(self.spacing)

        # create buttons...
        for index, size_name in enumerate(self.thumbnail_view_sizes):
            size = self.thumbnail_view_sizes[size_name]
            size_button = ImageSizeButton(
                parent=self, image_size=size, name=size_name, index=index
            )
            self.thumbnail_view_buttons[size_name] = size_button
            self.main_layout.addWidget(size_button)

        # set width
        width = ((size_button.height() + self.spacing)* len(iUtils.getSetting('IMAGE_SIZES'))) + 40
        self.setFixedWidth(width)


class ImageSizeButton(QPushButton):
    """
    Single button that allows users to change the size thumbnail_views
    displayed to them in the shader library

    @image_size: <int> size of thumbnail_view
    @name: <str> name of the size, this is truncated to the first
        character and displayed on the button
    @index: <int> index of size in the overall list, used to determine
        the size of the widget displayed to the user
    """
    def __init__(self, parent=None, image_size=None, name=None, index=None):
        super(ImageSizeButton, self).__init__(parent)
        self.setCheckable(True)
        self.setFlat(True)
        self.image_size = image_size
        self.name = name

        # setup widget size
        h = self.height()
        self.setFixedSize(h, h)

        # creates a 'core' and a 'border' to give the
        # illusion of different sized widgets
        core_size = (
            h - (math.fabs((index + 1 ) - len(iUtils.getSetting('IMAGE_SIZES'))) * 5)
        )
        self.border_width = (h - core_size) * .5

        # set style sheet
        #stylesheet = iUtils.createThumbnailSS(self.border_width, False)
        self.setStyleSheet(iUtils.createThumbnailSS(self.border_width, False))
        self.clicked.connect(self.setSelected)

    def clearUserSelection(self):
        """
        Clears the previous thumbnail selected by the user
        """
        thumbnail_view_widgets = self.parent().thumbnail_view_buttons
        for size_name in list(thumbnail_view_widgets.keys()):
            size_button = thumbnail_view_widgets[size_name]
            if size_button != self:
                size_button.setChecked(False)
                size_button.setStyleSheet(iUtils.createThumbnailSS(size_button.border_width, False))
        pass

    def setSelected(self):
        """
        Updates the thumbnail size of the directory views
        """
        # set up main widget properties
        model = iUtils.getModel(self)
        self.clearUserSelection()
        self.setStyleSheet(iUtils.createThumbnailSS(self.border_width, True))
        main_widget = gUtils.getMainWidget(self, 'Library')

        scroll_bar_width = main_widget.detailed_view.vscrollbar.width()
        splitter_width = main_widget.main_splitter_handle_width
        main_widget.working_area_widget.setMinimumWidth(
            self.image_size + scroll_bar_width + splitter_width)

        main_widget.detailed_view.vheader.setMinimumWidth(self.image_size  + scroll_bar_width)

        main_widget.image_size = self.image_size
        # update models
        model.updateViews()

    @property
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, border_width):
        self._border_width = border_width

    @property
    def image_size(self):
        return self._image_size

    @image_size.setter
    def image_size(self, image_size):
        self._image_size = image_size

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    widget = TopBarMainWidget()
    widget.show()
    sys.exit(app.exec_())