'''
Drop menu needs to populate based off of type sent to it
shader
    katana
    klf
    material (import as material)
    subnet

'''
import os
import json

from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

from cgqtpy.ImageLibrary import Utils


class ImageWidget(QLabel):
    '''
    temperature = property(get_temperature,set_temperature)
    @ImageWidget <QLabel> Meant to be used as a super class for the
        Main/Default Images.  These classes will be the object types for
        displaying contact sheet images to the user.

    @image_width: should be image size... of proxy images
    @proxy_file_extension: extension of proxy file
    @image_dir: directory containing the image sequence proxy
    @current_image: name of the current image being displayed proxy
    @json_file: full path to json file hosting all of the meta data
    @file_extension: extension of files to use
    '''
    def __init__(
        self,
        parent=None,
        json_file=None,
    ):
        super(ImageWidget, self).__init__(parent=parent)
        # boolean operator to determine if an image should be
        # selected/ deselected
        # True: do not flip | False:  flip the switch
        self._activated = False

    ''' PROPERTIES '''

    def isSelected(self):
        model = Utils.getModel(self)
        selection_list = model.metadata['selected']
        if self.json_file in selection_list:
            return True
        else:
            return False

    def setSelected(self):
        stylesheet = Utils.getSetting('IMAGE_SELECTED_SS')
        self.setStyleSheet(stylesheet)
        model = Utils.getModel(self)
        model.appendToSelectionList(self.json_file)

    def setUnselected(self):
        style_sheet = '''
            border-style: solid;\
            border-width:2px;\
            border-color: rgba(0,0,0,0)\
        '''
        self.setStyleSheet(style_sheet)
        model = Utils.getModel(self)
        model.removeFromSelectionList(self.json_file)

    '''
    button <QButton> current button being pressed
    '''
    @property
    def button(self):
        return self._button

    @button.setter
    def button(self, button):
        self._button = button

    '''
    image_list <list> list of all files in the directory of proxy image
    '''
    @property
    def proxyImageList(self):
        return self._proxy_image_list

    @proxyImageList.setter
    def proxyImageList(self, image_list):
        self._proxy_image_list = image_list

    '''
    image_index <int> index of sorted(list(os.listdir))
        of file in the proxy image directory ( proxyImageDir )
    '''
    @property
    def proxyImageIndex(self):
        return self._image_index

    @proxyImageIndex.setter
    def proxyImageIndex(self, image_index=0):
        self._image_index = image_index

    ''' image_width <int> '''
    @property
    def image_width(self):
        return self._image_width

    @image_width.setter
    def image_width(self, image_width):
        self._image_width = image_width

    ''' proxy_file_extension <str> '''
    @property
    def proxyFileExtension(self):
        return self._proxy_file_extension

    @proxyFileExtension.setter
    def proxyFileExtension(self, proxy_file_extension):
        self._proxy_file_extension = proxy_file_extension

    ''' file_extension '''
    @property
    def fileExtension(self):
        if hasattr(self, 'file_extension') is False:
            self._file_extension = '.exr'
        return self._file_extension

    @fileExtension.setter
    def fileExtension(self, file_extension):
        self._file_extension = file_extension

    ''' init_pos <QPoint>'''
    @property
    def initPos(self):
        return self._init_pos

    @initPos.setter
    def initPos(self, init_pos):
        self._init_pos = init_pos

    ''' image_dir <str> '''
    @property
    def proxyImageDir(self):
        return self._image_dir

    @proxyImageDir.setter
    def proxyImageDir(self, image_dir):
        '''
        name of the directory containing the image sequence
        '''
        self._image_dir = image_dir

    @property # str < file_name>
    def currentImage(self):
        return self._current_image

    @currentImage.setter
    def currentImage(self, current_image):
        '''
        current image is the local name of the image in the dir
        '''

        self._current_image = current_image

    @property # < QPixmap >
    def currentPixmap(self):
        return self.pixmap

    @currentPixmap.setter
    def currentPixmap(self, current_pixmap):
        '''
        the current image is a full file path to an image on disk
        '''
        self.pixmap = QPixmap(current_pixmap)
        self.pixmap = self.pixmap.scaledToWidth(self.image_width)
        self.setPixmap(self.pixmap)
        return self.pixmap

    @property # str < filepath >
    def json_file(self):
        return self._json_file

    @json_file.setter
    def json_file(self, json_file):
        self._json_file = json_file

    ''' UTILS '''

    def setImage(self, direction='next'):
        '''
        Displays the previous/next image to the user depending
        on the input given to direction
        @direction: <str> if it will display the next/previous image
        '''
        current_index = self.proxyImageIndex
        image_list = self.proxyImageList
        if direction is 'next':
            current_index += 1
        elif direction is 'previous':
            current_index -= 1
        new_image = image_list[current_index]
        proxy_image_dir = self.proxyImageDir
        new_image_path = '/'.join([proxy_image_dir, new_image])
        self.proxyImageIndex = current_index

        self.currentImage = new_image

        self.currentPixmap = new_image_path
        self.setFrameWidgetText(new_image)

    def nextImage(self):
        self.setImage(direction='next')

    def previousImage(self):
        self.setImage(direction='previous')

    ''' EVENTS '''

    def mousePressEvent(self, event, *args, **kwargs):
        self.button = event.button()
        main_widget = Utils.getMainWidget(self)

        # set selection
        #selection_list = self.model.metadata['selected']
        if event.button() == Qt.LeftButton:

            # set initial postion for drag slider
            pos = QCursor.pos()
            self.initPos = pos
            # model.updateViews()
        elif event.button() == Qt.MiddleButton:
                self.setSelected()

        main_widget.imageClickedEvent(event, self)

        return QLabel.mousePressEvent(self, event, *args, **kwargs)

    def mouseReleaseEvent(self, event, *args, **kwargs):
        # selection toggle used if the full screen has been activated
        if event.button() == Qt.LeftButton:
            if self._activated is False:
                if self.isSelected():
                    self.setUnselected()
                else:
                    self.setSelected()

            self._activated = False
        model = Utils.getModel(self)
        model.updateViews()
        # not to sure on why this goes bananas
        # RuntimeError: wrapped C/C++ object of type DefaultImage has been deleted
        # return QLabel.mouseReleaseEvent(self, event, *args, **kwargs)


class DefaultImage(ImageWidget):
    '''
    Displays the image to the user in the tab.  This is the image that is
    displayed in the contact sheet in the WrappingLayout
    '''
    def __init__(
        self,
        parent=None,
        image_width=None,
        json_file=None
    ):
        super(ImageWidget, self).__init__(parent)
        '''
        @image_dir : path to directory with image sequence inside
        '''
        self._activated = False

        self.json_file = json_file
        json_data = Utils.getJSONData(json_file)

        self.proxyImageDir = json_data['proxy']
        self.proxyImageList = (sorted(os.listdir(json_data['proxy'])))
        self.proxyImageIndex = 0

        self.image_width = image_width
        self.setFixedWidth(self.image_width)
        self.setFixedHeight(self.image_width)

        self.currentImage = os.listdir(self.proxyImageDir)[0]
        file_extension = self.currentImage[self.currentImage.rindex('.'):]
        self.proxyFileExtension = file_extension

        # set default image
        if 'default_image' in json_data.keys():
            current_image = '/'.join([self.proxyImageDir, json_data['default_image']])
            if os.path.isfile(current_image) is False:
                current_image = '/'.join([self.proxyImageDir, self.currentImage])
        else:
            current_image = '/'.join([self.proxyImageDir, self.currentImage])
        self.currentPixmap = current_image

        # set default style sheet
        style_sheet = '''
            border-style: solid;\
            border-width:2px;\
            border-color: rgba(0,0,0,0)\
        '''
        self.setStyleSheet(style_sheet)

    ''' EVENTS '''

    def mouseMoveEvent(self, event, *args, **kwargs):
        def leftMousePress():
            pos = QCursor.pos()
            init_pos = self.initPos.x()
            # mouse move distance
            mmd = init_pos - pos.x()
            activation_distance = 20
            '''
            change the image to the next one in the sequence
            based off of how far the mouse moves
            @mmd: how far the mouse has moved
            @change_distance: how far the mouse has to move
                before an update is trigger
            '''
            if mmd > activation_distance or mmd < -activation_distance:
                # Flip selected
                self.setSelected()
                self._activated = True
                # Activate full screen display
                main_widget = Utils.getMainWidget(self)
                main_widget.activateFullScreenDisplay()

        def rightMousePress():
            print('rmb')

        def middleMousePress():
            pass

        if self.button == Qt.LeftButton:
            leftMousePress()
        elif self.button == Qt.RightButton:
            rightMousePress()
        elif self.button == Qt.MiddleButton:
            middleMousePress()
        return QLabel.mouseMoveEvent(self, event, *args, **kwargs)

    '''
    def mouseReleaseEvent(self, event, *args, **kwargs):
        if self.button == Qt.LeftButton:
            model = Utils.getModel(self)
            model.updateViews()
            return ImageWidget.mouseReleaseEvent(self, event, *args, **kwargs)
    '''


class DropMenu(QDialog):
    '''
    Popup menu that is displayed when a user CTRL+Drag/Drops into
    the Nodegraph.  This will popup options for the user, if there are
    multiple options for them to select from.
    '''
    def __init__(
        self,
        parent=None,
        data_dir='',
        data_type=''
    ):
        super(DropMenu, self).__init__(parent)

        # set transparent bg
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setWindowFlags(
            self.windowFlags()
            ^ Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # set initial position
        pos = QCursor().pos()
        geo = self.geometry()
        self.setGeometry(pos.x(), pos.y(), geo.width(), geo.height())

        # set up gui
        layout = QVBoxLayout()
        self.setLayout(layout)

        something_list = os.listdir(data_dir)
        if data_type == 'shader':
            something_list.append('.material')
            something_list.append('.subnet')

        for x in something_list:
            text = x[x.rindex('.')+1:]
            button = TestButton(parent=self, text=text)
            layout.addWidget(button, QMessageBox.YesRole)
            style_sheet = "border:none"
            button.setStyleSheet(style_sheet)

        self.retval = self.exec_()

    def setButtonPressed(self, button):
        self.button_pressed = button.text()


class TestButton(QPushButton):
    def __init__(self, parent=None, text=''):
        super(TestButton, self).__init__(parent)
        self.setText(text)

    def mousePressEvent(self, *args, **kwargs):
        self.parent().setButtonPressed(self)
        self.parent().close()
        # return QPushButton.mousePressEvent(self, *args, **kwargs)
