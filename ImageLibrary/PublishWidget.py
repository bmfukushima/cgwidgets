import json
import sys

from qtpy.QtWidgets import *
from qtpy.QtCore import *

from cgqtpy.ImageLibrary import Utils


class PublishWidget(QWidget):
    '''
    @frame: <path to files> raw renders (exrs)
    @proxy: <path to files> downres renders (jpg)
    @data: <path to files> importable files
    @name: name
    @note: notes
    @default_image: <file name> default display image
    @type:
        texture
            textures containing multiple different types of maps
        shader <klf> <katana>
            pre built shading network (macro? lookfile? both?)
            json for shaderNetworkInterrupt
        lightrig <rig>
            Light Rig
        lighttex <texture>
            Textures meant to be plugged into lights
    '''
    def __init__(self, parent=None):
        super(PublishWidget, self).__init__(parent)
        # Container Style Sheet
        self.container_ss = Utils.getSetting('PUBLISH_CONTAINER_SS')

        # need to fix these options... ['rig', 'emit', 'block', 'hdri']
        self.publish_options = [
            {'display_name': 'Name', 'name': 'name', 'type': 'lineedit'},
            {'display_name': 'Publish Type',
             'name': 'type',
             'type': 'combobox',
             'options': ['shader', 'texture', 'lightrig', 'lighttex']
             },
            {'display_name': 'Frames Location', 'name': 'frame', 'type': 'lineedit'},
            {'display_name': 'Proxy Location', 'name': 'proxy', 'type': 'lineedit'},
            {'display_name': 'Location of Data', 'name': 'data', 'type': 'lineedit'},
            {'display_name': 'Notes', 'name': 'note', 'type': 'lineedit'},
            {'display_name': 'Default Image', 'name': 'default_image', 'type': 'lineedit'}
        ]

        self.publish_widgets = {}
        self.createGUI()

    ''' CREATE GUI '''

    def createGUI(self):
        '''
        creates the publish GUI
        @frame                    :                    raw renders (exrs)
        @proxy                    :                    downres renders (jpg)
        @data                      :                    importable files
        @name                    :                    name
        @note                      :                    notes
        @default_image      :                    default display image
        @type                      :
        '''
        # main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        self.createPublishParameters()
        self.createPublishGroup()

    def createContainer(self, title):
        container = QGroupBox()
        container.setTitle(title)
        container.setStyleSheet(self.container_ss)
        layout = QVBoxLayout()
        m = Utils.getSetting('PUBLISH_GROUP_CONTENT_MARGINS')
        layout.setContentsMargins(m, m, m, m)
        container.setLayout(layout)

        return container

    def createPublishParameters(self):
        '''
        Creates all the inputs for the user to fill in
        that will be embedded into the JSON file
        '''

        # create container
        container = self.createContainer('OPTIONS')

        # create user input widgets
        for option in self.publish_options:
            name = option['display_name']
            widget_type = option['type']
            if widget_type == 'lineedit':
                widget = UserInputLineEdit(name=name)
            else:
                dropdown_options = option['options']
                widget = UserInputDropDown(name=name, options=dropdown_options)
            container.layout().addWidget(widget)
            self.publish_widgets[option['name']] = widget

        self.layout().addWidget(container)

    def createPublishGroup(self):
        '''
        Creates the button the user pressed to publish the JSON
        file, and the input location for the user to determine where
        the JSON file will be saved
        '''
        # Create group container
        container = self.createContainer('PUBLISH')

        # add publish dir
        self.publish_dir = UserInputLineEdit(name='Publish Directory')
        container.layout().addWidget(self.publish_dir)

        # create publish button
        self.publish_button = QPushButton('Publish')
        self.publish_button.clicked.connect(self.publish)
        container.layout().addWidget(self.publish_button)
    
        # add container to main layout
        self.layout().addWidget(container)

    ''' UTILS '''

    def publish(self):
        '''
        publishes the json file to the location selected in the tree widget
        by the user
        '''
        publish_file = {}
        publish_file['iskatanalibrary'] = True
        for option in self.publish_widgets.keys():
            widget = self.publish_widgets[option]
            #name = widget.name
            value = widget.getValue()
            publish_file[option] = value

        filedir = self.publish_dir.getValue()
        with open(filedir, 'w') as f:
            json.dump(publish_file, f, sort_keys=True, indent=4)


class UserInput(QWidget):
    '''
    Default user input widget, this one consist of one row in the VBox

    @name: <str> name of the parameter displayed to the user
    '''
    def __init__(self, parent=None, name=None):
        super(UserInput, self).__init__(parent)

        layout = QHBoxLayout()
        self.label = QLabel(name)
        self.label.setFixedWidth(150)
        self.setLayout(layout)
        layout.addWidget(self.label)
        self.name = name

    def getValue(self):
        '''
        Abstract method for children, this will be required
        to return the call to get the values
        '''
        return 'If this is returning, you did it wrong'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name


class UserInputLineEdit(UserInput):
    def __init__(self, parent=None, name=None):
        super(UserInputLineEdit, self).__init__(parent, name=name)

        self.user_input = QLineEdit()
        self.layout().addWidget(self.user_input)

    def getValue(self):
        return self.user_input.text()


class UserInputDropDown(UserInput):
    def __init__(self, parent=None, name=None, options=[]):
        super(UserInputDropDown, self).__init__(parent, name=name)

        self.user_input = QComboBox()
        self.user_input.addItems(options)
        self.layout().addWidget(self.user_input)

    def getValue(self):
        return self.user_input.currentText()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = PublishWidget()
    main.show()
    sys.exit(app.exec_())
