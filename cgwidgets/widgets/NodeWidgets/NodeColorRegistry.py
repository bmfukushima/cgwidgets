"""
TODO (node color registry):
    *   Data containers
        *   How to store / load
                - How to handle filepaths?
                - Store data on KatanaProjectSettings (285, 293)
                - Callback/Event on init.py to check for this param, and on node create, set the color
                    - This param, will just be a filepath
                    - default filepath?  Create an environment variable to host the default filepath

TODO ( cgwidgets )
    *   Move str converter
            color = index.internalPointer().getArg("color")[1:-1].split(", ")
            color = [int(c) for c in color]
    *   Update color widget (194)
            Show correct color values when delegate is displayed
TODO ( wish list )
    *   Create Duplicate NodeType (DUPLICATE NODE TYPE)
            Expand to existing
"""
"""
The NodeColorRegistryWidget Widget allows users to easily set up node/color combinations and save
them out to a JSON file.  The purpose for these JSON files is that the map can then be
reused when nodes are created to create default node colors for various DCC's.

Reset Color:
    Control + MMB on any item

Data Locations:
    Data locations are stored under an environment variable.
    
    This environment variable can be set using "NodeColorRegistryWidget.setConfigsEnvar()", by default it is set
    to "CGWNODECOLORCONFIGS".  If the envar is not valid, it will default to the default save directory.  
    Which is set to cgwidgets.utils.getDefaultSavePath(), and can also be set using
    NodeColorRegistryWidget.setDefaultSaveLocation().

    will have all of its files checked for the extension ".json" and the key "COLORCONFIG" to determine
    if it is a valid color config.  Please note that subdirectories are not supported.
    
    The users can save/load these files using the UI provided in the NodeColorIOWidget.  An important thing to
    note about how the save paths are determines is that the "Dir" widget, is stored as a map called "envarMap"
    which contains the key/pairs for each directory name, and the full path on disk.  This means, that each
    directory name must be unique.

Data Structure:
    each item is stored as a dictionary which should look like:
    {
        "children": [],
        "color":"255, 255, 255, 255",
        "enabled": bool,
        "item_type":COLOR|GROUP,
        "name": item.getName()
    }

    {
    COLORCONFIG: TRUE,
    data : 
        [
            {
                "children": [dict(child_a), dict(child_b)],
                "color":"(255,255,255,255)",
                "enabled":bool,
                "item_type":COLOR|GROUP,
                "name": item.getName()
            },
            dict(child_c),
            dict(child_d)
        ]
    }

Hierarchy
    NodeColorRegistryWidget --> (QWidget | UI4.Tabs.BaseTab)
        |- QVBoxLayout
            |- node_colors_widget --> (ModelViewWidget)
            |    |- _node_type_creation_widget --> (NodeTypeListWidget)
            |    |- node_color_view --> (AbstractDragDropTreeView)
            |        |- delegate --> (NodeColorItemDelegate --> AbstractDragDropModelDelegate)
            |             |- column0 delegate --> (Default | NodeTypeListWidget)
            |             |- column1 delegate --> (ColorDelegate --> ColorInputWidget)
            | - _io_widget --> (NodeColorIOWidget)
                 |- QVBoxLayout
                     |- _color_configs_directory_labelled_widget --> (LabelledInputWidget)
                     |    |- _color_configs_directory_widget --> (ListInputWidget)
                     |- color_configs_files_labelled_widget --> (LabelledInputWidget)
                     |    |- _color_configs_files_widget --> (ListInputWidget)
                     |- QHBoxLayout
                          |- _load_button_widget --> (ButtonInputWidget)
                          |- _save_button_widget --> (ButtonInputWidget)

NodeColorViewItems args:
    node (str): name of the current node type or group
    item_type (int): GROUP | COLOR
    color (str): rgba255 ie (255,255,255,255)
    children (list): 
    enabled (bool): if the item is enabled or not

"""
import json
import math
import os

from qtpy.QtWidgets import QWidget, QVBoxLayout, QStyle, QHBoxLayout
from qtpy.QtCore import Qt, QModelIndex
from qtpy.QtGui import QColor, QPen
# from Katana import UI4

from cgwidgets.widgets import (
    NodeTypeListWidget,
    ShojiModelViewWidget,
    ModelViewWidget,
    ModelViewItem,
    ColorInputWidget,
    ButtonInputWidget,
    ListInputWidget,
    LabelledInputWidget
)
from cgwidgets.views import AbstractDragDropModelDelegate, AbstractDragDropTreeView, AbstractDragDropModel
from cgwidgets.utils import setAsTool, setAsAlwaysOnTop, centerWidgetOnCursor, getWidgetAncestor, getDefaultSavePath
from cgwidgets.settings import iColor, attrs

COLOR = "COLOR"
GROUP = "GROUP"


class ColorDelegate(ColorInputWidget):
    def __init__(self, parent=None):
        super(ColorDelegate, self).__init__(parent=parent)
        self.setHeaderPosition(position=attrs.NORTH)

    def text(self):
        return repr([str(x).zfill(3) for x in self.getColor().getRgb()])[1:-1].replace('\'', '')


class NodeColorItemDelegate(AbstractDragDropModelDelegate):
    """ The delegate for the main view.  This will open/close all of the different views
    that the user can open by double clicking on an item/column.

    Attributes:
        current_item (DragDropModelItem): currently being manipulated"""

    TYPE = 0
    COLOR = 1

    def __init__(self, parent=None):
        super(NodeColorItemDelegate, self).__init__(parent)

    def __userFinishedUpdatingNodeType(self, widget, node_type):
        """ Run whenever the user finishes editing this delegate"""
        color_registry_widget = getWidgetAncestor(self, NodeColorRegistryWidget)
        node_types = color_registry_widget.nodeTypes()

        if node_type not in widget.getAllTypes():
            self._current_item.setArg("name", self._previous_node_type)
            print("Invalid node type {node_type}".format(node_type=node_type))
            return
        if node_type == self._previous_node_type: return

        # node_type already exists, reset
        if node_type in node_types:
            # todo DUPLICATE NODE TYPE
            """ User has attempted to create a node type that already exists, go to
            the existing one"""
            self._current_item.setArg("name", self._previous_node_type)
            widget.setText(self._previous_node_type)

        # update node type
        else:
            color_registry_widget.appendNodeType(node_type)
            color_registry_widget.removeNodeType(self._previous_node_type)

    def updateEditorGeometry(self, editor, option, index):
        """ Updates the editors geometry.

        This is needed so that the COLOR delegate can popup in place
        """
        if index.column() == NodeColorItemDelegate.TYPE:
            return AbstractDragDropModelDelegate.updateEditorGeometry(self, editor, option, index)

        elif index.column() == NodeColorItemDelegate.COLOR:
            return

    def createEditor(self, parent, option, index):
        """ Creates the editor widget.

        This is needed to set a different delegate for different columns"""
        if index.column() == NodeColorItemDelegate.TYPE:
            item = index.internalPointer()
            if item.getArg("item_type") == GROUP:
                return AbstractDragDropModelDelegate.createEditor(self, parent, option, index)
            else:
                class NodeTypeListWidgetDelegate(NodeTypeListWidget):
                    """ Custom delegate for displaying the node types

                    This is needed so that during the show event, we can set the text nothing"""

                    def __init__(self, parent=None):
                        super(NodeTypeListWidgetDelegate, self).__init__(parent)

                    def showEvent(self, event):
                        self.setText("")
                        return NodeTypeListWidget.showEvent(self, event)

                delegate = NodeTypeListWidgetDelegate(parent)
                self._current_item = index.internalPointer()
                self._previous_node_type = self._current_item.getArg("name")
                delegate.setUserFinishedEditingEvent(self.__userFinishedUpdatingNodeType)
                return delegate

        elif index.column() == NodeColorItemDelegate.COLOR:
            delegate = ColorDelegate(parent)
            setAsAlwaysOnTop(delegate)
            delegate.show()

            setAsTool(delegate)
            delegate.resize(512+256, 512)
            centerWidgetOnCursor(delegate)

            # set color
            # todo (194) update color input widget on show
            """ This needs to set the crosshair at the correct position, and update the display
            of the gradient for the correct HSV values"""
            color = index.internalPointer().getArg("color").split(", ")
            color = [int(c) for c in color]
            delegate.setColor(QColor(*color))
            # delegate.updateDisplay()

            return delegate
        pass

    def paint(self, painter, option, index):
        """ Custom paint event to override the existing handler for this style

        This is needed as StyleSheets/Data won't mix, and the stylesheet will
        automatically overwrite the data() set on the model

        https://stackoverflow.com/questions/39995688/set-different-color-to-specifc-items-in-qlistwidget
        """
        # return if disabled
        if not index.internalPointer().isEnabled():
            super(NodeColorItemDelegate, self).paint(painter, option, index)
            return

        if index.column() == 1:
            painter.save()

            # draw BG
            try:
                color = index.internalPointer().getArg("color").split(", ")
                color = [int(c) for c in color]
            except:
                color = iColor["rgba_background_01"]
            bg_color = QColor(*color)
            painter.setBrush(bg_color)
            painter.drawRect(option.rect)

            # draw selection border
            if option.state & QStyle.State_Selected:
                # If the item is selected, always draw background red
                color = iColor["rgba_selected"]
            else:
                color = iColor["rgba_black"]

            painter.setPen(QPen(QColor(*color)))
            painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
            painter.drawLine(option.rect.topLeft(), option.rect.topRight())
            painter.drawLine(option.rect.topRight(), option.rect.bottomRight())

            # draw text color
            """ Text color will be drawn dynamically based off of the value
            of the existing widget."""
            if bg_color.value() < 64 or 192 < bg_color.value():
                text_color = [
                    int(math.fabs(bg_color.red() - 255)),
                    int(math.fabs(bg_color.green() - 255)),
                    int(math.fabs(bg_color.blue() - 255)),
                    255]
                text_color = QColor(*text_color)
                text_color = QColor(text_color.value(), text_color.value(), text_color.value(), 255)
            else:
                int_color = int(math.fabs(bg_color.value() - 128))
                text_color = [
                    int_color,
                    int_color,
                    int_color,
                    255
                ]
                text_color = QColor(*text_color)
            painter.setPen(text_color)
            text = index.data(Qt.DisplayRole)
            option.rect.setLeft(option.rect.left() + 5)
            painter.drawText(option.rect, int(Qt.AlignLeft | Qt.AlignVCenter), text)
            # painter.drawText(option.rect, (Qt.AlignLeft | Qt.AlignVCenter), text)

            painter.restore()
        else:
            super(NodeColorItemDelegate, self).paint(painter, option, index)
        return


class NodeColorView(AbstractDragDropTreeView):
    def __init__(self, parent=None):
        super(NodeColorView, self).__init__(parent)
        # self.setIsDeletable(True)

    def mouseReleaseEvent(self, event):
        """ Reset color on CTRL+MMB"""
        if event.modifiers() == Qt.ControlModifier:
            if event.button() == Qt.MiddleButton:
                index = self.indexAt(event.pos())
                item = index.internalPointer()
                if item:
                    item.setArg("color", "")

        return AbstractDragDropTreeView.mouseReleaseEvent(self, event)

    def keyPressEvent(self, event):
        """ On G Key Press, create group"""
        if event.key() == Qt.Key_G:
            selected_indexes = self.getAllSelectedIndexes()
            column_data = {"name": "group", "color": "", "item_type": GROUP}

            # create new group from selection
            if 0 < len(selected_indexes):
                parent = selected_indexes[0].parent()
                row = selected_indexes[0].row()

                # create new group item
                new_group_index = self.model().insertNewIndex(row, name="group", column_data=column_data,
                                                              is_dropable=True, parent=parent)
                new_group_item = new_group_index.internalPointer()

                # reparent selected items under the new group
                for row, index in enumerate(selected_indexes):
                    item = index.internalPointer()
                    self.model().setItemParent(row, item, new_group_index)

                    # get unique name
                    unique_name = AbstractDragDropModel.getUniqueItemName(item)
                    item.setArg("name", unique_name)

            # create new group
            else:
                row = self.model().getRootItem().childCount()
                new_group_index = self.model().insertNewIndex(row, name="group", column_data=column_data,
                                                              is_dropable=True)
                new_group_item = new_group_index.internalPointer()

            # update new group items unique name
            unique_name = AbstractDragDropModel.getUniqueItemName(new_group_item)
            new_group_item.setArg("name", unique_name)
            # self.model().layoutChanged.emit()

            # self.update(new_group_index)

        if event.key() == Qt.Key_E:
            data_dict = self.exportModelToDict(self.rootItem())
            print(data_dict)

        return AbstractDragDropTreeView.keyPressEvent(self, event)


class NodeColorIOWidget(QWidget):
    """ Widget that will contain all of the I/O functionality.

    Attributes:
        configs_directory (str): the current path on disk to a directory containing color config files
        default_save_location (str): path on disk that will be the default save directory
            if the environment variable is not valid.
        envar (str): environment variable that contains directories that will hold config files
        envar_map (dict): a map of names/locations to map the envar directory to its full path.
            This is used when saving/loading.
        file_name (str): name of the current file
        save_path (str): full path on disk to current save directory
    TODO
            *   Set environment variable
            *   Get directories from environment variable
            *   Store a dictionary of keypair values, for the environment variable,
                and the directory names
            *   On Load / save
                    Get directory path that should be loaded / saved."""
    def __init__(self, parent=None, envar="CGWNODECOLORCONFIGS"):
        super(NodeColorIOWidget, self).__init__(parent)

        # setup default attrs
        self._envar = envar
        self._envar_map = {}
        self._default_save_location = getDefaultSavePath()
        self._configs_directory = ""
        self._file_name = ""

        # create widgets
        self._color_configs_directory_widget = ListInputWidget()
        self._color_configs_directory_widget.setCleanItemsFunction(self.__getConfigDirectories)
        self._color_configs_directory_widget.setUserFinishedEditingEvent(self.__userUpdatedColorDirectories)
        self._color_configs_directory_labelled_widget = LabelledInputWidget(
            name="Dir", delegate_widget=self._color_configs_directory_widget)

        self._color_configs_files_widget = ListInputWidget()
        self._color_configs_files_widget.setCleanItemsFunction(self.__getAllColorConfigFiles)
        self._color_configs_files_widget.setUserFinishedEditingEvent(self.__userUpdatedColorFile)
        self._color_configs_files_labelled_widget = LabelledInputWidget(
            name="File", delegate_widget=self._color_configs_files_widget)

        self._load_button_widget = ButtonInputWidget(
            title="LOAD", user_clicked_event=self.loadEvent, flag=False, is_toggleable=False)
        self._save_button_widget = ButtonInputWidget(
            title="SAVE", user_clicked_event=self.saveEvent, flag=False, is_toggleable=False)

        # setup layout IO Layout
        self._io_layout = QHBoxLayout()
        self._io_layout.addWidget(self._load_button_widget)
        self._io_layout.addWidget(self._save_button_widget)

        # setup main layout
        QVBoxLayout(self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._color_configs_directory_labelled_widget)
        self.layout().addWidget(self._color_configs_files_labelled_widget)
        self.layout().addLayout(self._io_layout)

    """ PROPERTIES """
    def defaultSaveLocation(self):
        return self._default_save_location

    def setDefaultSaveLocation(self, default_save_location):
        self._default_save_location = default_save_location

    def configsDir(self):
        return self._configs_directory

    def setConfigsDir(self, configs_dir):
        self._configs_directory = configs_dir

    def configsEnvar(self):
        return self._envar

    def setConfigsEnvar(self, envar):
        """ Sets the name of the environment variable to search for configs in

        This envar will have a list of directories that will contain config (json) files.

        Args:
            envar (str): environment variable
                By default this is set to CGWNODECOLORCONFIGS"""
        self._envar = envar

    def envarMap(self):
        return self._envar_map

    def addEnvarMapItem(self, directory_name, full_path):
        self.envarMap()[directory_name] = full_path

    def fileName(self):
        return self._file_name

    def setFileName(self, file_name):
        self._file_name = file_name

    def savePath(self):
        """ The full path on disk for the config to be loaded/saved"""
        if self.configsDir() in self.envarMap().keys():
            save_path = "{directory}/{file_name}.json".format(
                directory=self.envarMap()[self.configsDir()],
                file_name=self.fileName()
            )
            return save_path

        return None
    """ UTILS """
    @staticmethod
    def isColorConfigFile(path):
        """ Determines if the path provided is a Color Config or not

        Args (path): Full path on disk to color config file

        Returns (bool)"""
        if path:
            if os.path.isfile(path):
                if path.endswith(".json"):
                    with open(path, "r") as filepath:
                        data = json.load(filepath)
                        if "COLORCONFIG" in data.keys():
                            return True
        return False

    """ EVENTS """
    def saveEvent(self, widget):
        export_data = self.nodeColorRegistryWidget().getExportData()
        if self.savePath():
            if self.configsDir() and self.fileName():
                with open(self.savePath(), "w") as filepath:
                    json.dump(export_data, filepath)
                    print("Saving color config to \n\t|-{path}".format(path=self.savePath()))
                    return
        print("{path} is not a valid color config file".format(path=self.savePath()))
        # todo (285) KATANA on save, set filepath parameter on RootNode

    def loadEvent(self, widget):
        if self.configsDir() and self.fileName():
            if NodeColorIOWidget.isColorConfigFile(self.savePath()):
                if os.path.isfile(self.savePath()):
                    self.nodeColorRegistryWidget().loadColorFile(self.savePath())
                    print("Loading color config from \n\t|-{path}".format(path=self.savePath()))
                    return

        print("{path} is not a valid color config file".format(path=self.savePath()))

    def __getConfigDirectories(self):
        """ When the user clicks on the Directories widget, this will:
                1.) populate the directories list
                2.) Update the envar map
        """
        # if envar doesn't exist
        if self.configsEnvar() not in os.environ.keys():
            directories = [self.defaultSaveLocation()]

        # if envar exists
        else:
            directories = os.environ[self.configsEnvar()].split(";")

        # run through the full directories and:
        #   1.) make the envar map
        #   2.) make the returnable directories list
        _dir_list = []
        for full_path in directories:
            full_path = full_path.rstrip("/").rstrip("\\")
            dir_name = os.path.basename(full_path)
            self.addEnvarMapItem(dir_name, full_path)
            _dir_list.append([dir_name])

        return _dir_list

    def __userUpdatedColorDirectories(self, widget, value):
        """ When the user updates the directories widget, this will update the files available."""
        if value not in self.envarMap().keys():
            widget.setText(self.configsDir())
            return
        if value == self.configsDir(): return

        self.setConfigsDir(value)
        self.colorConfigsFilesListWidget().setText("")

    def __getAllColorConfigFiles(self):
        """ Gets all of the color config files in the directory provided.

        This will check each file to see if its:
            1.) A JSON File
            2.) Has the key COLORCONFIG

        Args:
            path (str): path on disk to directory to check
        """
        # key exists
        if self.configsDir() in self.envarMap().keys():
            dir = self.envarMap()[self.configsDir()]

            color_configs = []
            for file_name in os.listdir(dir):
                full_path = "{dir}/{name}".format(dir=dir, name=file_name)
                if NodeColorIOWidget.isColorConfigFile(full_path):
                    color_configs.append([file_name.replace(".json", "")])

            return color_configs
        # key doesn't exist
        else:
            return []

    def __userUpdatedColorFile(self, widget, value):
        """ User has just finished updating the file path"""
        self.setFileName(value)

    """ WIDGETS """
    def colorConfigsFilesListWidget(self):
        return self._color_configs_files_widget

    def colorConfigsDirectoriesListWidget(self):
        return self._color_configs_directory_widget

    def nodeColorRegistryWidget(self):
        return getWidgetAncestor(self, NodeColorRegistryWidget)

    def colorFilesWidget(self):
        return self._color_files_widget

    def saveWidget(self):
        return self._save_button_widget

    def loadWidget(self):
        return self._load_button_widget


class NodeColorRegistryWidget(QWidget):
    """Main widget for the Node Color Registry."""

    def __init__(self, parent=None, envar="CGWNODECOLORCONFIGS"):
        super(NodeColorRegistryWidget, self).__init__(parent)

        # setup default attributes
        self._node_types = []

        # create GUI
        self.__setupGUI(envar)

    def __setupGUI(self, envar):
        """ Sets up the main GUI for this widget """
        # create main view widget
        self._node_colors_widget = ModelViewWidget(self)

        # setup view
        self._node_color_view = NodeColorView(self)
        self._node_colors_widget.setView(self._node_color_view)
        self._node_color_view.setItemExportDataFunction(self.getItemExportData)
        self._node_colors_widget.model().setHeaderData(['name', 'color'])
        self._node_colors_widget.setMultiSelect(True)

        # setup item delegate
        delegate = NodeColorItemDelegate(self)
        self._node_colors_widget.view().setItemDelegate(delegate)

        # setup node creation widget
        self._node_type_creation_widget = NodeTypeListWidget(self)
        self._node_colors_widget.addDelegate([], self._node_type_creation_widget, modifier=Qt.NoModifier, focus=True)
        self._node_type_creation_widget.show()

        # setup events
        # self._node_colors_widget.setIndexSelectedEvent(self.selectionChanged)
        self._node_colors_widget.setTextChangedEvent(self.nameChangedEvent)
        self._node_colors_widget.setItemDeleteEvent(self.deleteItem)
        self._node_type_creation_widget.setUserFinishedEditingEvent(self.createNewColorEvent)

        # setup load / save buttons
        self._io_widget = NodeColorIOWidget(self, envar=envar)

        # setup layout
        QVBoxLayout(self)
        self.layout().addWidget(self.nodeColorsWidget())
        self.layout().addWidget(self.ioWidget())
        self.layout().setStretch(0, 1)
        self.layout().setStretch(1, 0)

    """ PROPERTIES """
    def configsEnvar(self):
        return self.ioWidget().configsEnvar()

    def setConfigsEnvar(self, envar):
        """ Sets the name of the environment variable to search for configs in

        This envar will have a list of directories that will contain config (json) files.

        Args:
            envar (str): environment variable
                By default this is set to CGWNODECOLORCONFIGS"""
        self.ioWidget().setConfigsEnvar(envar)

    def defaultSaveLocation(self):
        return self.ioWidget().defaultSaveLocation()

    def setDefaultSaveLocation(self, default_save_location):
        self.ioWidget().setDefaultSaveLocation(default_save_location)

    def nodeTypes(self):
        return self._node_types

    def appendNodeType(self, node_type):
        self._node_types.append(node_type)

    def removeNodeType(self, node_type):
        self._node_types.remove(node_type)

    def resetNodeTypes(self):
        self._node_types = []

    """ UTILS """
    def getExportData(self):
        export_data = {"COLORCONFIG": True}
        export_data.update(self.nodeColorsWidget().exportModelToDict(self.nodeColorsWidget().rootItem()))
        return export_data

    def populate(self, children, parent=QModelIndex()):
        """ Populates the view

        Args:
            children (list): of item data"""
        for child in reversed(children):
            if child["item_type"] == COLOR:
                # column_data = child
                new_index = self.nodeColorsWidget().insertNewIndex(
                    0, name=child["name"], column_data=child, is_dropable=False, parent=parent)
                self.appendNodeType(child["name"])
            elif child["item_type"] == GROUP:
                new_index = self.nodeColorsWidget().insertNewIndex(
                    0, name="group", column_data=child, is_dropable=True, parent=parent)
                self.populate(child["children"], parent=new_index)
                pass

            # setup enable/disabled
            if not child["enabled"]:
                new_item = new_index.internalPointer()
                new_item.setIsEnabled(child["enabled"])

    def loadColorFile(self, filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)["data"]

                # clear model
                self.nodeColorsWidget().clearModel()
                self.resetNodeTypes()

                # populate model
                self.populate(data)

            # todo (293) KATANA on load, set filepath parameter on RootNode
        except FileNotFoundError:
            # Todo file does not exist.

            pass

    """ EVENTS """
    def deleteItem(self, item):
        """ Removes the selected item from the model.

        This will check all of the descendants for any node types,
        and remove them from the internal nodeTypes list"""
        # get all children
        descendents = self.nodeColorView().getItemsDescendants(item)
        descendents.append(item)
        for child in descendents:
            if child.getArg("item_type") == COLOR:
                print("removing ...", child.getArg("name"))
                self.removeNodeType(child.getArg("name"))

    def getItemExportData(self, item):
        """ Individual items dictionary when exported.

        Note:
            node has to come first.  This is due to how the item.name() function is called.
            As if no "name" arg is found, it will return the first key in the dict"""
        return {
            "name": item.getArg("name"),
            "children": [],
            "color": item.getArg("color"),
            "enabled": item.isEnabled(),
            "item_type": item.getArg("item_type")

        }

    def nameChangedEvent(self, item, old_value, new_value):
        item_name = AbstractDragDropModel.getUniqueItemName(item)
        if new_value != item_name:
            item.setName(item_name)

    def selectionChanged(self, item, enabled):
        if enabled:
            print(item.getArg("name"), item.getArg("color"), item.getArg("item_type"))

    def createNewColorEvent(self, widget, value):
        """ Creates a new node type index """
        node_type = value

        if self.nodeTypeCreationWidget().text() == "": return
        if value in self.nodeTypes():
            # todo DUPLICATE NODE TYPE
            """ User has attempted to create a node type that already exists, go to
            the existing one"""
            return

        # all_nodes = NodegraphAPI.GetNodeTypes()
        all_nodes = [node[0] for node in self.nodeTypeCreationWidget().getCleanItems()]

        if node_type in all_nodes:
            column_data = {"name": node_type, "color": "", "item_type": COLOR}
            new_index = self.nodeColorsWidget().insertNewIndex(
                0, name=node_type, column_data=column_data, is_dropable=False)
            self.appendNodeType(node_type)
        self._node_type_creation_widget.setText("")

    def __createNewNodeColorItem(self, node_type, default_color=None):
        pass

    """ WIDGETS """

    def ioWidget(self):
        return self._io_widget

    def nodeTypeCreationWidget(self):
        return self._node_type_creation_widget

    def nodeColorsWidget(self):
        return self._node_colors_widget

    def nodeColorView(self):
        return self._node_color_view


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication
    from cgwidgets.utils import centerWidgetOnScreen

    app = QApplication(sys.argv)
    os.environ["CGWNODECOLORCONFIGS"] = "/home/brian/.cgwidgets/colorConfigs_01/;/home/brian/.cgwidgets/colorConfigs_02"
    #os.environ["CGWNODECOLORCONFIGS"] = "/home/brian/.cgwidgets/colorConfigs_01/;/home/brian/.cgwidgets/colorConfigs_02"

    node_color_registry = NodeColorRegistryWidget()
    setAsAlwaysOnTop(node_color_registry)
    node_color_registry.show()
    centerWidgetOnScreen(node_color_registry)

    sys.exit(app.exec_())