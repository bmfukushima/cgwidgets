'''
need to clean up..
    - move all document all methods/properties in classes
    - move to UML chart eventually...
- iUtils and Settings iUtils are going to conflict...
    - and then add the Settings tab?

API:
    Drag/Drop...
        eventType(tab, method)
            ie
                dropEvent(NodegraphTab, test)

BUGS TO SQUASH

    - Drag/drop shaders with
    - Drag/drop w/modifier
    - Drop menu doesnt exist anymore...

FullScreenImageItem
    - To QWidget
        QStackedLayout
            ImageWidget
            Qlabel ( notes )
            QLabel ( frame )

FullScreenImage
    - Continue drag selection from image widget...?
    - Resize issue not getting all pixels available...
        _ FullScreenImageViewer --> getImageSize
        - Only when 1 column or row
        - only on minimum width/height?


IMPORT SYSTEM
Need to rethink the entire lightrig/lighttex import system...
    Potential API for additional types?
    Right now lighttex drag/drop into GafferThree just imports the rig...

Need to rethink data grabbing for dropping...
    ImageWidget --> mousePressEvent
    the proxy image replace on file path will cause issues with drag/dropping
    the parameters boxes...
        if not named correctly will just not work lol

Drag/Drop for file paths
    UDIM for texture param drop
        WIll need to detect if it has UDIMs...
    Sequence for texture frame drop event...
        Will need to detect if it has a sequence...
        ImageWidget --> mousePressEvent
    - Is it safe to assume that the last '.' will always be status quo?

PUBLISH SYSTEM
Add Top Bar?
    Do I even care? Should the user even have this?
    MainWidget --> createGUI -->
            HBOX
                Library Directory
                    library_dir
                    - Default read from environment variable
                    - Add string so users can change, environment variable populates this?

DefaultImage
    Font Size...
        Watch out for this... ImageLabels
            Being Truncated on the width...

Publish Widget...
    - When toggling back/forth needs to adjust the minimum width
            TopBarWidget --> PublishToggleButton --> togglePublishMode
    - Text needs to be updated with system text for minimum label size...
            publishWidget --> createGUI
            Where is event for font size changed?

#===============================================================================
# IDEA
#===============================================================================

#===============================================================================
# To Do
#===============================================================================
full_screen_widget
    is this showing the actual resolution?  Me no thinky so?

send frames to bottom left...
    going to bottom of widget right now... not bottom of pixmap =\

#===============================================================================
# WISH LIST
#===============================================================================
- Arrow Key next/previous image
    A/S --> only works on full screen
        need to expand to all in selection?
- \\ Search Filter
- \\ Display Image name/frame
- \\ Display label for pixmaps
#===============================================================================
# HACKs
#===============================================================================
keyPressEvent doesnt work for some widgets? Overrwritten with a QShortcut
    1.) QShortcut(QKeySequence("Ctrl+D"), self.nodegraphTab, self.setSelectedNode)
gafferThreeEditor event filter...
    does not get inherited by the parameters panels "_installEventFilterForChildWidgets"

#===============================================================================
# SETUP PIPELINE DIRECTORY
#===============================================================================
$LIBRARY_DIR:
    Need to set this environment variable to add this into your pipeline.
    This will automatically populate all of the directories in this variables

$PYTHONPATH:
    - qtpy needs to be install
    - Need to update your PYTHONPATH to include qtpy
#===============================================================================
# JSON META DATA
#===============================================================================

json_dump = {     'frame': '/media/ssd01/library/tempfiles/templates/card/frame',
                            'proxy' : '/media/ssd01/library/tempfiles/templates/card/proxy',
                            'data' : '/media/ssd01/library/tempfiles/templates/card/data',
                            'type' : '<type>'             ,
                            'default_image' : '<default image>' ,
                            'notes' : '<notes>'
                     }

required:
@frame: <dir> full resolution images
@proxy: <dir> proxy resolution images
@data: <dir> importable data types
@type: <str> arbitrary data type
optional:
@default_image <file name> image to display by default
@notes: <str> user comments/notes'

#===============================================================================
# Events
#===============================================================================
light
    emit
        \\parameter  --> drag/drop paths
        \\gaffer  --> drag/drop create area light
        \\nodegraph --> drag/drop create gaffer
    block
        \\parameter --> drag/drop paths
        \\gaffer  -->drag/drop create filter
        \\nodegraph --> drag/drop create gaffer
    hdri
        \\parameter --> drag/drop paths
        \\gaffer --> drag/drop create env light
        \\nodegraph --> drag/drop create gaffer
    rig
        \\nodegraph --> create gaffer
        \\gaffer --> import rig

lookdev
    shader
        \\ nodegraph --> import
        subnet --> import portion of graph... and insert...
    texture
        \\nodegraph --> create shading node
            does single shading node, needs to evolve a
            smarter system into doing multiple shading nodes
        \\ parameter --> path

NOTES:
    json file needs iskatanalibrary key to be registered for plugin
'''
import re

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

#from cgqtpy.ImageLibrary import ImageWidget
import sys
from . import ImageWidget
from .PublishWidget import PublishWidget
from .TopBarWidget import TopBarMainWidget
from .__utils__ import iUtils
from cgwidgets import __utils__ as gUtils
from .Views import *


class LibraryWidget(QWidget, iUtils):
    '''
    @selection_list: a list of Image Widgets to display
        which ones are currently selected
    '''

    def __init__(self, parent=None):
        super(LibraryWidget, self).__init__(parent)
        self._is_full_screen_display = False
        self._temp_selection_list = []
        self._drop_action_list = []
        self.createGUI()
        self.setupShortcuts()

    def __name__(self):
        return 'Library'

    def setupShortcuts(self):
        # Shortcuts
        QShortcut(
            QKeySequence("Escape"),
            self.full_screen_image,
            self.closeFullScreenImageWidget
        )
        """
        QShortcut(
            QKeySequence("Q"),
            self.full_screen_image,
            self.full_screen_image.displayFrameWidget
        )
        QShortcut(
            QKeySequence("W"),
            self.full_screen_image,
            self.full_screen_image.displayNoteWidget
        )
        QShortcut(
            QKeySequence("D"),
            self.full_screen_image,
            self.full_screen_image.nextImage
        )
        QShortcut(
            QKeySequence("A"),
            self.full_screen_image,
            self.full_screen_image.previousImage
        )
        """

    def setupWorkingArea(self):
        # set up right side of slider
        self.working_area_widget = QWidget()

        self.working_area_main_layout = QVBoxLayout()
        self.working_area_main_layout.setContentsMargins(0, 0, 0, 0)
        self.working_area_layout = QStackedLayout()

        self.working_area_layout.setAlignment(Qt.AlignTop)
        # self.working_area_layout.setContentsMargins(0,0,0,0)
        # setup widgets
        self.search_bar = SearchBar()
        self.publish_widget = PublishWidget()
        # setup views
        self.thumbnail_view = ThumbnailViewWidget(self)
        self.detailed_view = DetailedViewWidget(self)
        self.list_view = ListViewMainWidget(self)

        # add widgets to working area layout
        self.working_area_layout.addWidget(self.thumbnail_view)
        self.working_area_layout.addWidget(self.detailed_view)
        self.working_area_layout.addWidget(self.list_view)
        self.working_area_layout.addWidget(self.publish_widget)

        # add widgets/layouts
        self.working_area_widget.setLayout(self.working_area_main_layout)
        self.working_area_main_layout.addLayout(self.working_area_layout)
        self.working_area_main_layout.addWidget(self.search_bar)
        return self.working_area_layout

    def createGUI(self):
        # ATTRIBUTES

        # how large each image will be in the thumbnail_view sheet
        # This is going to change... and be hosted in settings...

        # setup main layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.top_bar_widget = TopBarMainWidget(self)

        # Main View
        self.view_layout = QStackedLayout()
        self.main_splitter = QSplitter()
        self.main_splitter_handle_width = 10
        self.main_splitter.setHandleWidth(self.main_splitter_handle_width)
        #self.full_screen_image = ImageWidget.FullScreenImage()
        self.full_screen_image = FullScreenImageViewer(self)
        '''
        self.full_screen_image_layout = QVBoxLayout()
        self.full_screen_image.setLayout(self.full_screen_image_layout)
        self.full_screen_image.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        '''

        self.view_layout.addWidget(self.main_splitter)
        self.view_layout.addWidget(self.full_screen_image)

        # set up dir list
        self.library_dir = os.environ['LIBRARY_DIR']
        self.dir_widget = DirList(library_dir=self.library_dir)
        self.setupWorkingArea()

        # add widgets
        self.main_splitter.addWidget(self.dir_widget)
        self.main_splitter.addWidget(self.working_area_widget)
        self.main_splitter.setSizes([200, 600])

        # add widgets to main layout
        self.main_layout.addWidget(self.top_bar_widget)
        self.main_layout.addLayout(self.view_layout)

        # setup user defaults
        self.setupUserDefaults()

    def setupUserDefaults(self):
        '''
        Sets up the user defaults for any options the user may click
        in the interface
        '''
        self.model = ImageListModel(parent_widget=self)
        # Default View
        mode_widget = self.top_bar_widget.mode_container.mode_menu
        default_view = iUtils.getSetting('DEFAULT_VIEW')
        mode_index = mode_widget.model().findItems(default_view, Qt.MatchExactly)
        try:
            row = mode_index[0].index().row()
        except IndexError:
            row = 0
        mode_widget.setCurrentIndex(row)

        # Default Size
        size_layout = self.top_bar_widget.size_button_container.main_layout
        for index in range(size_layout.count()):
            widget = size_layout.itemAt(index).widget()
            widget_size_name = widget.name
            default_size = iUtils.getSetting('DEFAULT_SIZE')
            if widget_size_name == default_size:
                widget.setSelected()

    '''  UTILS '''

    def getSelectionList(self):
        return self.model.metadata['selected']

    def getFullScreenImageWidget(self):
        return self.full_screen_image

    def closeFullScreenImageWidget(self):
        self.view_layout.setCurrentIndex(0)

    ''' API '''

    @property
    def library_dir(self):
        return self._library_dir

    @library_dir.setter
    def library_dir(self, library_dir):
        self._library_dir = library_dir

    @property
    def drag_image_path(self):
        '''
        Path to the image, upon drop this will be the text
        that is dropped into text editable fields
        '''
        return self._drag_image_path

    @drag_image_path.setter
    def drag_image_path(self, drag_image_path):
        self._drag_image_path = drag_image_path

    @drag_image_path.deleter
    def drag_image_path(self):
        del self._drag_image_path

    @property
    def drag_proxy_image_path(self):
        '''
        path to proxy image to be displayed to the user
        during a drag operation
        '''
        return self._drag_proxy_image_path

    @drag_proxy_image_path.setter
    def drag_proxy_image_path(self, drag_proxy_image_path):
        self._drag_proxy_image_path = drag_proxy_image_path

    @drag_proxy_image_path.deleter
    def drag_proxy_image_path(self):
        del self._drag_proxy_image_path

    @property
    def drop_action_list(self):
        return self._drop_action_list

    @drop_action_list.setter
    def drop_action_list(self, drop_action_list):
        self._drop_action_list = drop_action_list

    def add_drop_action(self, widget_list, method):
        '''
        @widget_list: <list> of widgets to install the event filter on
        @method: <fun> method to run during the drop event
        '''
        self.drop_action_list.append(
            {
                'widget_list': widget_list,
                'method': method
            }
        )

    def imageClickedEvent(self, event, widget):
        '''
        @event: <QEvent> mousePressEvent
        @widget: <ImageWidget> the current image that the user has
            clicked on with the middle mouse button

            This is meant to be overwritten when the you subclass this
            bad boy... if you want some of that sweet sweet drag/drop
            functionality
        '''
        if widget.button == Qt.MiddleButton:
            '''
            install event filters
            '''
            for action in self.drop_action_list:
                widget_list = action['widget_list']
                # method = action['method']
                for w in widget_list:
                    w.removeEventFilter(self)
                    w.installEventFilter(self)
            '''
            get the image displayed to the user during the drag operation
            and the path to the file location if it is dropped in a text field
            '''
            try:
                self.drag_image_path
                self.drag_proxy_image_path
            except AttributeError:
                json_data = gUtils.getJSONData(widget.json_file)
                if 'default_image' in json_data.keys():
                    current_image = '/'.join([widget.proxyImageDir, json_data['default_image']])
                    if os.path.isfile(current_image) is False:
                        current_image = '/'.join([widget.proxyImageDir, widget.currentImage])
                else:
                    current_image = '/'.join([widget.proxyImageDir, widget.currentImage])
                self.drag_image_path = current_image
                self.drag_proxy_image_path = current_image

            drag = QDrag(self)

            # set drag/drop pixmap
            pixmap = QPixmap(self.drag_proxy_image_path)
            pixmap = pixmap.scaledToWidth(widget.image_width * .5)
            drag.setPixmap(pixmap)
            hotspot = QPoint(pixmap.width() * .5, pixmap.height() * .5)
            drag.setHotSpot(hotspot)

            # set drag/drop data
            mime_data = QMimeData()
            mime_data.setText(self.drag_image_path)
            drag.setMimeData(mime_data)

            # execute drag/drop
            drag.exec_(Qt.MoveAction)

            # reset attrs
            del self.drag_image_path
            del self.drag_proxy_image_path
        return

    def eventFilter(self, obj, event, *args, **kwargs):
        if event.type() in (
            QEvent.DragEnter,
            QEvent.DragMove,
            QEvent.Drop
        ):
            if event.type() != QEvent.Drop:
                event.acceptProposedAction()
            else:
                for action in self.drop_action_list:
                    widget_list = action['widget_list']
                    for widget in widget_list:
                        if widget == obj:
                            action['method']
            return True
        return QWidget.eventFilter(self, obj, event, *args, **kwargs)

    def mouseReleaseEvent(self, *args, **kwargs):
        print("mouse release event ( library )")
        return QWidget.mouseReleaseEvent(self, *args, **kwargs)
    ''' PROPERTIES '''

    @property
    def temp_selection_list(self):
        return self._temp_selection_list

    @temp_selection_list.setter
    def temp_selection_list(self, temp_selection_list):
        self._temp_selection_list = list(temp_selection_list)

    @property
    def image_size(self):
        return self._image_size

    @image_size.setter
    def image_size(self, image_size):
        self._image_size = image_size

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, model):
        self._model = model
        self.thumbnail_view.setModel(model)
        self.detailed_view.setModel(model)

    ''' EVENTS '''

    def activateFullScreenDisplay(self):
        '''
        Gets the current list of items selected by the user
        and displays them full screen in contact sheet format
        '''
        view_layout = self.view_layout
        if view_layout.currentIndex() == 0:
            self.view_layout.setCurrentIndex(1)
            # store temp selection list
            self.temp_selection_list = self.model.metadata['selected']

            # set up full screen widget
            full_screen_image_table = self.full_screen_image
            full_screen_image_table.update(self.model.metadata['selected'])

            # activate full screen widget

    def resizeEvent(self, *args, **kwargs):
        # why is the thumbnail view updating here?
        # self.thumbnail_view.update()
        return QWidget.resizeEvent(self, *args, **kwargs)


class FullScreenImageViewer(ThumbnailViewWidget):
    '''
    Widget that is displayed when the user click/drags on a
    thumbnail a certain distance to activate.

    Hit escape to close.  There is no other way to go back, because
    I really don't think it's worth wasting the screen real estate on that...
    '''
    def __init__(self, parent=None):
        super(FullScreenImageViewer, self).__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setToolTip('''
    LMB Click:
        Select image ( If the border is yellow, the image is considered to be "selected")
    LMB Click + Drag:
        Drag direction:
            Left: Previous Image
            Right: Next Image
        Modifiers:
            Alt: All Selected Images
            Ctrl: Only image clicked
            None: All images
    MMB Click + Drag:
        Drop into a tab to get the desired results for each DCC.
        ''')

    def getImageSize(self):
        '''
        Gets the max image height/width based off of the algo here:
        https://math.stackexchange.com/questions/466198/algorithm-to-get-the-maximum-size-of-n-squares-that-fit-into-a-rectangle-with-a/466248
        '''

        # get attributes
        n = len(gUtils.getMainWidget(self, 'Library').temp_selection_list)
        if n == 0:
            '''
            small hack, when the widget is initializing it will try to divide by 0
            This is just a hack to force it not to make any errors... 
            '''
            return 1
        x = self.width()
        y = self.height()

        # calculate offset for spacing + border widths
        image_selected_border_width= iUtils.getSetting('IMAGE_SELECTED_BORDER_WIDTH')
        border_width = image_selected_border_width
        if n == 1:
            offset = border_width
        else:
            offset = (self.spacing*.5) + (border_width * .5)
        # Compute number of rows and columns, and cell size
        ratio = x / y
        ncols_float = math.sqrt(n * ratio)
        nrows_float = n / ncols_float

        # // Find best option filling the whole height
        nrows1 = math.ceil(nrows_float)
        ncols1 = math.ceil(n / nrows1)

        while nrows1 * ratio < ncols1:
            nrows1 += 1
            ncols1 = math.ceil(n / nrows1)

        cell_size1 = y / nrows1

        # Find best option filling the whole width
        ncols2 = math.ceil(ncols_float)
        nrows2 = math.ceil(n / ncols2)
        while (ncols2 < nrows2 * ratio):
            ncols2 += 1
            nrows2 = math.ceil(n / ncols2)

        cell_size2 = x / ncols2

        # Find best values
        if (cell_size1 < cell_size2):
            nrows = nrows2
            ncols = ncols2
            cell_size = cell_size2
        else:
            nrows = nrows1
            ncols = ncols1
            cell_size = cell_size1
        self.num_columns = ncols

        # something needs to happen here?
        if ( ncols == 1 and nrows > 1 ) or (ncols > 1 and nrows == 1):
            #offset = ( n - 1 )* ((self.spacing*.5) + (border_width * .5))
            offset = (( n )* (border_width)) + 4
            #offset = border_width * 4
        cell_size -= offset

        return cell_size

    def createModelFromSelectionList(self, selection_list=None):
        '''
        creates a new model for itself based off of the user selection
        that is stored in the main model
        '''
        view_list = []
        model = ImageListModel(parent_widget=self)
        for filepath in selection_list:
            view_list.append(filepath)
        model.populateModelFromList(view_list)
        return model

    def update(self, selection_list):
        model = self.createModelFromSelectionList(selection_list=selection_list)
        self.image_size = self.getImageSize()
        self.setModel(model)

        # update selected items...
        for widget in self.widget_list:
            if widget.isSelected():
                widget.setSelected()
            else:
                widget.setUnselected()

    def setModel(self, model):
        self.model = model
        # reset
        # create temp list to store current images
        temp_dict = {}
        for index in range(self.main_layout.count()):
            widget = self.main_layout.itemAt(index).widget()
            temp_dict[widget.json_file] = {}
            temp_dict[widget.json_file]['currentImage'] = widget.currentImage
            temp_dict[widget.json_file]['proxyImageIndex'] = widget.proxyImageIndex
        # clear layout
        gUtils.clearLayout(self.main_layout)

        # populate model
        widget_list = []

        for row in range(model.rowCount()):
            jsondata = model.imageJSONList[row]
            # check to see if there is a current image...
            try:
                default_values = temp_dict[jsondata['filepath']]
            except KeyError:
                default_values = None
                # if it cannot find the key, then it will go boop
                pass
            image_widget = FullScreenImageItem(
                parent=self,
                image_width=self.image_size,
                json_file=jsondata['filepath'],
                default_values=default_values
            )

            widget_list.append(image_widget)

        self.widget_list = widget_list
        self.layoutWidgets(num_columns=self.num_columns)

    ''' PROPERTIES '''

    @property
    def widget_list(self):
        return self._widget_list

    @widget_list.setter
    def widget_list(self, widget_list):
        self._widget_list = widget_list

    def appendToImageList(self, widget):
        self._image_list.append(widget)

    ''' EVENTS '''
    def nextImage(self, selected=True):
        '''
        sets the next image for all selected images
        @selected: <bool> if True, will only set the next image
            of the selected image.  If False, will update ALL images
        '''
        for widget in self.widget_list:
            if selected is True:
                if widget.isSelected() is True:
                    widget.nextImage()
            else:
                widget.nextImage()

    def previousImage(self, selected=True):
        '''
        sets the previous image for all selected images
        @selected: <bool> if True, will only set the previous image
            of the selected image.  If False, will update ALL images
        '''
        #image_list = iUtils.getModel(self).metadata['selected']
        for widget in self.widget_list:
            if selected is True:
                if widget.isSelected() is True:
                    widget.previousImage()
            else:
                widget.previousImage()

    def hideEvent(self, *args, **kwargs):
        '''
        When this widget is hidden from view, it returns the
        previous selection back to the user
        '''
        main_widget = gUtils.getMainWidget(self, 'Library')
        main_widget.model.metadata['selected'] = main_widget.temp_selection_list
        main_widget.model.updateViews()
        return ThumbnailViewWidget.hideEvent(self, *args, **kwargs)

    def resizeEvent(self, event, *args, **kwargs):
        '''
        When this widget is resized, it updates the sizes of the widgets
        to get the most possible space
        '''
        main_widget = gUtils.getMainWidget(self, 'Library')
        self.update(selection_list=main_widget.temp_selection_list)
        #return ThumbnailViewWidget.resizeEvent(self, event, *args, **kwargs)


class FullScreenImageItem(ImageWidget.ImageWidget):
    def __init__(
        self,
        parent=None,
        image_width=None,
        json_file=None,
        default_values=None
    ):
        super(FullScreenImageItem, self).__init__(parent)

        # set up json data

        self.json_file = json_file
        json_data = gUtils.getJSONData(json_file)

        self.image_width = image_width

        # set up default image
        self.proxyImageDir = json_data['proxy']
        self.proxyImageList = (sorted(os.listdir(json_data['proxy'])))

        # check to see if default image exists already
        if not default_values:
            self.proxyImageIndex = 0
            self.currentImage = os.listdir(self.proxyImageDir)[0]
        else:
            self.currentImage = default_values['currentImage']
            self.proxyImageIndex = default_values['proxyImageIndex']

        # set default image
        if 'default_image' in json_data.keys():
            current_image = '/'.join(
                [self.proxyImageDir, json_data['default_image']]
            )
            if os.path.isfile(current_image) is False:
                current_image = '/'.join([self.proxyImageDir, self.currentImage])
        else:
            current_image = '/'.join([self.proxyImageDir, self.currentImage])
        self.currentPixmap = current_image

        # get file extension
        file_extension = self.currentImage[self.currentImage.rindex('.'):]
        self.proxyFileExtension = file_extension

        # create text widget
        self.text_widget = QLabel(self)

        # set note
        self.setToolTip(repr(json_data).replace(',', '\n')[1:-1])

        # settings
        self.setFixedWidth(self.image_width)
        self.setFixedHeight(self.image_width)

        self.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )

        FULL_SCREEN_TEXT_SS = iUtils.getSetting('FULL_SCREEN_TEXT_SS')
        style_sheet = FULL_SCREEN_TEXT_SS
        self.text_widget.setStyleSheet(style_sheet)

    def setFrameWidgetPosition(self):
        frame_widget = self.getFrameWidget()
        frame_y_pos = (
            self.geometry().bottomLeft().y()
            - frame_widget.geometry().height()
        )
        frame_rect = frame_widget.geometry()
        frame_widget.setGeometry(
            0,
            frame_y_pos, frame_rect.width(),
            frame_rect.height()
        )

    def getFrameWidget(self):
        return self.text_widget

    def setFrameWidgetText(self, text):
        text = text[:text.rindex('.')]
        text_widget = self.getFrameWidget()
        text_widget.setText(text)
        self.text_widget.adjustSize()

    def displayFrameWidget(self):
        # Q pressed
        text_widget = self.getFrameWidget()
        if text_widget.isHidden() is True:
            text_widget.show()
        else:
            text_widget.hide()

    def getNoteWidget(self):
        return self.note_widget

    def setNoteWidgetText(self, text):
        note_widget = self.getNoteWidget()
        note_widget.setFixedWidth(self.imageWidth)
        note_widget.setText(text)
        self.note_widget.adjustSize()

    def displayNoteWidget(self):
        # w pressed
        note_widget = self.getNoteWidget()
        if note_widget.isHidden() is True:
            note_widget.show()
        else:
            note_widget.hide()

    def mouseMoveEvent(self, event, *args, **kwargs):
        try:
            pos = QCursor.pos()
            init_pos = self.initPos.x()
            # mouse move distance
            mmd = init_pos - pos.x()
            change_distance = 20
            if mmd > change_distance or mmd < -change_distance:
                self._activated = True
                modifiers = QApplication.keyboardModifiers()
                # Determine which image to use
                # control modifer, do single image
                if modifiers == Qt.ControlModifier:
                    # update the image
                    if mmd > change_distance:
                        self.previousImage()
                    elif mmd < -change_distance:
                        self.nextImage()
                    self.initPos = pos
                # do all images
                else:
                    # Alt modifer will toggle between all selected images and all images
                    if modifiers == Qt.AltModifier:
                        selected = True
                    else:
                        selected = False

                    # update the image
                    main_widget = gUtils.getMainWidget(self, 'Library')
                    full_screen_view = main_widget.full_screen_image
                    if mmd > change_distance:
                        full_screen_view.previousImage(selected=selected)
                    elif mmd < -change_distance:
                        full_screen_view.nextImage(selected=selected)
                    self.initPos = pos

        except AttributeError:
            # error if this is not a mmb event
            pass
        return QLabel.mouseMoveEvent(self, event, *args, **kwargs)


class ListViewMainWidget(QScrollArea):
    '''
    primary layout of the contact sheet
    '''
    def __init__(self, parent=None):
        super(ListViewMainWidget, self).__init__(parent)

        self.top_level_widget = QWidget()
        self.setWidgetResizable(True)
        self.setWidget(self.top_level_widget)

        layout = QVBoxLayout()
        label = QLabel("List View... Coming soooooon")
        layout.addWidget(label)
        self.top_level_widget.setLayout(layout)

    def update(self):
        pass


class SearchBar(QLineEdit):
    '''
    bottom search bar
    used by user to filter the search results being display to them
    '''
    def __init__(self, parent=None):
        super(SearchBar, self).__init__(parent)
        self.setToolTip('''
    Search Bar:
        columnname{regex, regex}
            ie
        name{test}
            This will search will search for everything
            that has the word 'test' in the name column.

    Multiple Selection:
        columnname{regex, regex}columnname{regex, regex}

        In order to search multiple columns simulatenously,
        you can continue to use special tolkens.
            name{regex,regex}
                ie
            name{brian}type{isawesome}

    Note:
        This uses the re.search() funcionality for matching.

        Hit "enter" or "return" to update...

        if ANY searches match, it will display the item

        Any items selected will remain selected when searching,
        this is only a display update.
        ''')

    def keyPressEvent(self, event, *args, **kwargs):
        '''
        On Enter/Return:
            Will update all of the views based on the parameters
            specified by the user.
        '''
        accepted_keys = [Qt.Key_Enter, Qt.Key_Return]
        if event.key() in accepted_keys:
            model = iUtils.getModel(self)
            model.populateHideList(self.text())
            model.updateViews()

        return QLineEdit.keyPressEvent(self, event, *args, **kwargs)


class DirList(QTreeWidget):
    '''
    View of all of the sub directories of the location specified in
    library_dir.

    Library_dir is being parsed as an arg from the main
    widgets init function when this widget is instantiated.
    This should potentially be moved to an environment variable,
    as well as having a user defined location?
    '''
    def __init__(self, library_dir=None, parent=None):
        super(DirList, self).__init__(parent)
        # self.main_widget = main_widget
        self.setHeaderHidden(True)
        self.setAlternatingRowColors(True)
        #self.library_dir = library_dir
        for directory in library_dir.split(':'):
            self.populate(directory)

    def populate(self, directory):
        '''
        Creates all of the items for the model to replicate a hierarchical
        representation of the file system
        '''
        def populateChildren(item=None, directory=None):
            children = os.listdir(directory)
            if len(children) > 0:
                for name in os.listdir(directory):
                    new_directory = '/'.join([directory, name])
                    # check to see if its a dir, or display
                    if os.path.isdir(new_directory) is True:
                        new_item = DirListItem(
                            parent=item,
                            name=name,
                            file_dir=new_directory
                        )
                        if len(os.listdir(new_directory)) > 0:
                            populateChildren(
                                item=new_item,
                                directory=new_directory
                            )
                            new_item.setExpanded(True)

            return item

        root = self.invisibleRootItem()
        name = directory.split('/')[-1]
        item = DirListItem(
            parent=root,
            name=name,
            file_dir=directory
        )
        populateChildren(item=item, directory=directory)

    def selectionChanged(self, *args, **kwargs):
        '''
        When the user clicks on a new location, this will update the
        views to display all of the images located in that directory
        and its subdirectories in the view
        '''
        main_widget = gUtils.getMainWidget(self, 'Library')

        # get all items
        item = self.currentItem()
        children = self.getAllChildren(item, item_list=[])
        children.append(item)

        # populate views
        model = ImageListModel(
            parent_widget=self,
            filedirs_list=[item.getFileDir() for item in children]
        )
        main_widget.model = model

        return QTreeWidget.selectionChanged(self, *args, **kwargs)

    def getAllChildren(self, item, item_list=[]):
        if item.childCount() > 0:
            for index in range(0, item.childCount()):
                child = item.child(index)
                item_list.append(child)
                if child.childCount() > 0:
                    self.getAllChildren(child, item_list=item_list)
        return item_list


class DirListItem(QTreeWidgetItem):
    def __init__(self, parent=None, name='', file_dir=None):
        super(DirListItem, self).__init__(parent)
        self.setText(0, name)
        self.setFileDir(file_dir)
        # SET TEXT COLOR
        # self.setForeground(0,QBrush(QColor(200,200,200)))

    def setFileDir(self, file_dir):
        self.file_dir = file_dir

    def getFileDir(self):
        return self.file_dir


if __name__ == '__main__':

    app = QApplication(sys.argv)
    os.environ['LIBRARY_DIR'] = '/media/ssd01/library/library:/media/ssd01/library/library'
    main_widget = LibraryWidget()
    main_widget.show()
    sys.exit(app.exec_())

