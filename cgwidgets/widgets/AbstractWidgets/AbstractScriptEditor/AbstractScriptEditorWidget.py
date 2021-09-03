"""
#===============================================================================
# HotkeyDesign
#===============================================================================


                ScriptEditorWidget (Widget)
                hbox
                Splitter
                v---------------------------------------------------------v
            ScriptTreeWidget(Tree)                                      widget 
            BaseItem                                                    vbox 
            v--------------------v-----------------v                    v-------------------------------------------------v
        HotkeyDesignBaseItem       ScriptItem    ScriptMasterItem        MainTab (Tab)                                 SaveButton (Button)
    v----------------------v                                            v----------------------v
HotkeyDesignMasterItem        HotkeyDesignItem                                      code (PlainText)    HotkeyDesign (Widget)
                                                                                            PushButton Array


#===============================================================================
# WISH LIST
#===============================================================================
- Hotkeys...
    - Remove master design item as hotkey...
            - renameFile has a hack patch right now to fix this...
- Moving item to group does NOT update master hotkey file...
    
- Add save path...
    - How to have this work on larger networks with multiple Katana Resources?

- Add fifth row of fingers for '5tgb'


- Multi Gesture...
    Always reset display to center of the screen
        - Will this work on tablets?
#--------------------------------------------------------------------------- OLD
# IRF Support
    - if modifier hit... create it as an IRF and apply it?
    - Modifer Support?
# Unique hashes are getting split as string/ints... would be good to standardize a data format
    for them if they are to remain as key/pair values... probably ints?

# scripts master item
    create utils file
        first tab = utils
        second tab = python
            or 
        first tab = utils
        python tabs are now popup?

    how to automatically source this in? as it wont be in the same standard dir structure?


# figure out QApp stuff... just using imp to load atm

#Drag/Drop Slow
    Due to setting flags...
    Populating list is fine... its running through flags which causes the slight delay?

    Could just collapse the item and disable it, then re-expand it?


# could potentially use a hot key for previous/next? instead of groups?
    - easier for dumb dumbs...
    - technically less combinations
        (multiplication vs exponents)

# Stop HotkeyDesigns from being able to drop on themselves?
"""

import sys
import os
import math
import shutil
import json

from qtpy.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QWidget,
    QSplitter,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QItemDelegate,
    QMessageBox,
    QTabWidget,
    QPlainTextEdit,
    QMenu

)
from qtpy.QtCore import QVariant, Qt
from qtpy.QtGui import QCursor, QKeySequence

from cgwidgets.utils import getWidgetAncestor

from AbstractScriptEditorUtils import Utils as Locals
from AbstractScriptEditorWidgets import (
    HotkeyDesignEditorButton,
    HotkeyDesignEditorWidget,
    GestureDesignEditorWidget,
    GestureDesignButtonWidget)


class AbstractPythonEditor(QWidget):
    """ Default Python editor widget

    For each DCC this will need to be subclassed.  Where the codeWidget()
    will need to return access to the QPlainTextEdit, or w/e widget holds
    the user input portion of the editor"""
    def __init__(self, parent=None):
        super(AbstractPythonEditor, self).__init__(parent)

        layout = QVBoxLayout(self)
        self._code_widget = QPlainTextEdit(self)
        layout.addWidget(self._code_widget)

    def codeWidget(self):
        return self._code_widget


class ScriptEditorWidget(QWidget):
    """ Script Editors main widget

    Attributes:
        currentItem (item):
        filepath (str):
        python_editor (QWidget): to be displayed when editing Python Scripts
        scripts_variable (str): Environment Variable that will hold all of the locations
            that the scripts will be located in"""
    def __init__(self, parent=None, python_editor=AbstractPythonEditor, scripts_variable="CGWscripts"):
        super(ScriptEditorWidget, self).__init__(parent)
        self._scripts_variable = scripts_variable

        # self._file_path = KatanaResources.GetUserKatanaPath() + '/scripts'
        self._file_path = '/media/ssd01/dev/katana/KatanaResources_old/Scripts'
        if not os.path.exists(self._file_path):
            os.mkdir(self._file_path)
        if not os.path.exists(self._file_path + '/scripts'):
            os.mkdir(self._file_path + '/scripts')
        if not os.path.exists(self._file_path + '/designs'):
            os.mkdir(self._file_path + '/designs')
        if not os.path.exists(self._file_path + '/hotkeys.json'):
            hotkey_dict = {}
            with open(self._file_path + '/hotkeys.json', 'w') as f:
                json.dump(hotkey_dict, f)

        self.__setupGUI(python_editor)

    def __setupGUI(self, python_editor):
        """ Sets up the main GUI"""
        # MAIN LAYOUT
        self.layout = QHBoxLayout(self)
        self.splitter = QSplitter()
        self.layout.addWidget(self.splitter)

        # CREATE WIDGETS
        self._script_widget = ScriptTreeWidget(parent=self)
        self._design_tab_widget = DesignTab(parent=self, python_editor=python_editor)
        save_button = SaveButton(parent=self)

        self._design_main_widget = QWidget()
        design_vbox = QVBoxLayout()
        self._design_main_widget.setLayout(design_vbox)
        design_vbox.addWidget(self._design_tab_widget)
        design_vbox.addWidget(save_button)

        # ADD WIDGETS TO SPLITTER
        self.splitter.addWidget(self._script_widget)
        self.splitter.addWidget(self._design_main_widget)

    def __name__(self):
        return "ScriptEditorWidget"

    """ WIDGETS """
    def designMainWidget(self):
        return self._design_main_widget

    def designTabWidget(self):
        return self._design_tab_widget

    def scriptWidget(self):
        return self._script_widget

    """ PROPERTIES """
    def currentItem(self):
        return self._current_item

    def setCurrentItem(self, current_item):
        self._current_item = current_item

    def scriptsEnvar(self):
        return self._scripts_variable

    def setScriptsEnvar(self, variable):
        self._scripts_variable = variable

    def filepath(self):
        return self._file_path

    def setFilepath(self, file_path):
        self._file_path = file_path

    # def resizeEvent(self, event, *args, **kwargs):
    #     design_tab = self.designTabWidget()
    #     design_tab.updateAllGestureDesignsGeometry()
    #     return QWidget.resizeEvent(self, event, *args, **kwargs)


class SaveButton(QPushButton):
    """ Save button at the bottom of the Designer portion.

    This is used to save designs/scripts.
    """
    def __init__(self, parent=None):
        super(SaveButton, self).__init__(parent)
        self.setText('Save')
        self.clicked.connect(self.saveScript)
        script_editor_widget = getWidgetAncestor(self, ScriptEditorWidget)

        # check file paths exist
        file_path = script_editor_widget.filepath()
        if not os.path.isdir(file_path):
            os.mkdir(file_path)
        if not os.path.isdir(file_path + '/scripts'):
            os.mkdir(file_path + '/scripts')
        if not os.path.isdir(file_path + '/designs'):
            os.mkdir(file_path + '/designs')

    def __name__(self):
        return '__save_button__'

    def saveScript(self):
        """Saves the current script to disk"""
        script_editor_widget = getWidgetAncestor(self, ScriptEditorWidget)
        if hasattr(script_editor_widget, 'current_item'):
            current_item = script_editor_widget.currentItem()
            if current_item.getItemType() == 'script':
                text_block = script_editor_widget.designTabWidget().codeWidget()
                text = text_block.toPlainText()
                current_file = open('%s' % (current_item.filepath()), 'w')
                current_file.write(text)
                current_file.close()


class ScriptTreeWidget(QTreeWidget):
    """
    This tree widget sits on the left side of GUI and holds the list
    of all of the scripts/designs for the user to adjust
    """
    def __init__(self, parent=None):
        super(ScriptTreeWidget, self).__init__(parent)

        # set up attributes
        script_editor_widget = getWidgetAncestor(self, ScriptEditorWidget)
        self.setFilepath(script_editor_widget.filepath())
        self.head = self.header()
        header_widget = QTreeWidgetItem(['Name', 'Type', 'Hotkey'])
        self.setHeaderItem(header_widget)
        self.accepts_inputs = False

        # set flags
        self.setAlternatingRowColors(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.InternalMove)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

        # connect signals
        self.itemChanged.connect(self.renameFile)
        item_delegate = DataTypeDelegate(self)
        self.setItemDelegate(item_delegate)

        # Populate Items
        # Setup Master Items ( Top Level )
        self.scripts_item = ScriptMasterItem(
            self,
            filepath=script_editor_widget.filepath(),
            text='Scripts',
            unique_hash='master_scripts'
        )
        self.design_item = HotkeyDesignMasterItem(
            self,
            filepath=script_editor_widget.filepath(),
            text='Designs',
            unique_hash='master'
        )

        # Populate Items from Directories
        self.item_dict = {}
        self.populateItems()

        root_item = self.invisibleRootItem()
        root_item.setFlags(root_item.flags() & ~ Qt.ItemIsDropEnabled)

    def __name__(self):
        return '__script_list__'

    def populateItems(self):
        def populateDir(file_dir, parent_item):
            # sort directory
            dir_dict = {}
            for path in os.listdir(file_dir):
                name = path[path.index('.')+1:]
                dir_dict[name] = path

            for key in sorted(list(dir_dict.keys())):
                file = dir_dict[key]
                file_path = file_dir + '/%s' % file
                if '.' in file:
                    if file != 'master.py' and file != 'master.json':
                        if os.path.isdir(file_path):
                            unique_hash, text = file.replace('.py', '').split('.')
                            item = GroupItem(
                                parent_item,
                                text=text,
                                unique_hash=unique_hash,
                                file_dir=file_dir
                            )
                            self.item_dict[str(unique_hash)] = item
                            populateDir(file_path, item)
                        elif os.path.isfile(file_path):
                            if '.pyc' in file:
                                pass
                            else:
                                file_type = Locals().checkFileType(file_path)
                                if file_type == 'hotkey':
                                    unique_hash, text = file.replace('.json', '').split('.')
                                    item = HotkeyDesignItem(
                                        parent_item,
                                        text=text.replace('.json', ''),
                                        unique_hash=unique_hash,
                                        file_dir=file_dir
                                    )

                                elif file_type == 'gesture':
                                    unique_hash, text = file.replace('.json', '').split('.')
                                    item = GestureDesignItem(
                                        parent_item,
                                        text=text.replace('.json', ''),
                                        unique_hash=unique_hash,
                                        file_dir=file_dir
                                    )

                                elif file_type == 'script':
                                    unique_hash, text = file.replace('.py', '').split('.')
                                    item = ScriptItem(
                                        parent_item,
                                        text=text.replace('.py', ''),
                                        unique_hash=unique_hash,
                                        file_dir=file_dir
                                    )
                                self.item_dict[str(unique_hash)] = item

                        # set display hotkey
                        if file_path in list(hotkey_dict.keys()):
                            item.setText(2, hotkey_dict[file_path])
        hotkey_dict = Locals().getFileDict(self._file_path + '/hotkeys.json')
        populateDir(self._file_path + '/scripts', self.scripts_item)
        populateDir(self._file_path + '/designs', self.design_item)

    def getAllChildren(self, item, child_list=[]):
        """ Get all children/grandchildren of specified item

        Args:
            item (item): to search from
            child_list (list): list of items to be returned """
        if item.childCount() > 0:
            for index in range(item.childCount()):
                child = item.child(index)
                child_list.append(child)
                self.getAllChildren(child, child_list=child_list)
        else:
            child_list.append(item)

        return child_list

    def createNewItem(self, current_parent, item_type=None):
        """
        creates a new item under the current parent
        this item is based off of the item_type provided
        @current_parent <QTreeWidgetItem>
        @item_type <str>
        """
        file_dir = current_parent.getFileDir()
        if isinstance(current_parent, GroupItem):
            file_dir = current_parent.filepath()
        if item_type != 'group':
            if item_type == 'script':
                item = ScriptItem(current_parent, file_dir=file_dir)
            elif item_type == 'hotkey':
                item = HotkeyDesignItem(current_parent, file_dir=file_dir)
            elif item_type == 'gesture':
                item = GestureDesignItem(current_parent, file_dir=file_dir)
            self.getItemDict()[str(item.getHash())] = item
        elif item_type == 'group':
            item = GroupItem(current_parent, text='Group', file_dir=file_dir)

    def getItemDict(self):
        return self.item_dict

    def checkParentType(self, item):
        if item.parent():
            return self.checkParentType(item.parent())
        else:
            return item

    """ PROPERTIES """
    def setFilepath(self, file_path):
        self._file_path = file_path

    def filepath(self):
        return self._file_path

    """ UPDATE """
    def updateItem(self, current_item, new_file_dir, old_file_dir):
        """
        
        """
        # update file dir
        if hasattr(current_item, 'file_path'):
            if current_item.filepath() != None:
                file_path = current_item.filepath().replace(old_file_dir, new_file_dir)
                current_item.setFilepath(file_path)
                current_item.setFileDir(new_file_dir)

                # update design files
                script_editor_widget = getWidgetAncestor(self, ScriptEditorWidget)
                self.updateAllDesigns(
                    script_editor_widget.filepath() + '/designs',
                    new_file_dir,
                    old_file_dir
                )
                self.updateAllButtons()

    def updateAllItemPaths(self, current_item, new_file_dir, old_file_dir):
        """
        when a group name is changed, this function changes the file paths
        of all of the children/grand children recursively
        """
        for index in range(current_item.childCount()):
            child = current_item.child(index)
            self.updateItem(child, new_file_dir, old_file_dir)
            if isinstance(child, GroupItem):
                if current_item.childCount() > 0:
                    self.updateAllItemPaths(child, new_file_dir, old_file_dir)

    def updateGroup(self, current_item, new_file_dir=None, old_file_dir=None):
        """
        @current_item: <GroupItem> Current TreeWidgetItem selected by
        the user that has been altered
        @new_file_dir: <str> the new directory
        @new_file_dir: <str> the old directory
        """
        old_file_name = current_item.getFileName()
        old_file_path = current_item.filepath()

        if old_file_dir == None:
            old_file_dir = current_item.getFileDir()

        if new_file_dir == None:
            new_file_dir = current_item.parent().getFileDir()
            new_file_name = '%s.%s' % (current_item.getHash(), current_item.text(0))
            new_file_path = old_file_path.replace(old_file_name, new_file_name)
        else:
            new_file_name = current_item.getFileName()
            new_file_path = old_file_path.replace(old_file_dir, new_file_dir)

        current_item.setFilepath(new_file_path)
        current_item.setFileName(new_file_name)
        current_item.setFileDir(new_file_dir)

        # ===================================================================
        # update
        # ===================================================================
        # rename file
        if not os.path.exists(new_file_path):
            os.rename(old_file_path, new_file_path)
        # update design files
        script_editor_widget = getWidgetAncestor(self, ScriptEditorWidget)
        self.updateAllDesigns(
            script_editor_widget.filepath() + '/designs',
            new_file_path,
            old_file_path
        )

        # update all items
        self.updateAllItemPaths(current_item, new_file_path, old_file_path)
        # update all executable buttons
        self.updateAllButtons()
        # update design tab paths
        script_editor_widget.designTabWidget().updateTabFilePath(new_file_path, old_file_path)

    def renameFile(self):
        """
        poorly named function... should be named "renameItem" however... this
        will trigger all updates on the name change of an item
        rename file / update design paths / update buttons
        """
        def updateItem(current_item):
            # ===============================================================
            # rename file
            # ===============================================================
            old_file_name = current_item.getFileName()
            file_extension = old_file_name[old_file_name.rindex('.') + 1:]
            unique_hash = current_item.getHash()

            # in here to bypass the master for now...
            if unique_hash == 'master':
                return
            new_name = current_item.text(0)

            file_name = '%s.%s.%s' % (unique_hash, new_name, file_extension)

            current_item.setFileName(file_name)
            old_file_path = current_item.filepath()

            # this line will break... needs item file path
            new_file_path = '%s/%s' % (
                current_item.getFileDir(), current_item.getFileName()
            )
            current_item.setFilepath(new_file_path)
            if not os.path.exists(new_file_path):
                os.rename(old_file_path, new_file_path)
            # ===============================================================
            # set tab name
            # ===============================================================
            if (
                isinstance(current_item, HotkeyDesignItem)
                or isinstance(current_item, GestureDesignItem)
            ):
                # set tab name
                script_editor_widget = getWidgetAncestor(self, ScriptEditorWidget)
                design_tab = script_editor_widget.designTabWidget()
                tab_bar = design_tab.tabBar()
                for index in range(tab_bar.count()):
                    widget = design_tab.widget(index)
                    if hasattr(widget, 'getItem'):
                        if widget.getItem().getHash() == current_item.getHash():
                            design_tab.setTabText(index, current_item.text(0))
                            widget.setFilepath(new_file_path)
            # ===============================================================
            # rename buttons
            # ===============================================================
            if (
                isinstance(current_item, ScriptItem)
                or isinstance(current_item, HotkeyDesignItem)
                or isinstance(current_item, GestureDesignItem)
            ):
                script_editor_widget = getWidgetAncestor(self, ScriptEditorWidget)
                design_tab = script_editor_widget.designTabWidget()
                design_tab.updateAllHotkeyDesigns()
            return

        current_item = self.currentItem()
        if isinstance(current_item, ScriptMasterItem):
            return
        if current_item:
            # check to see if it is a name change
            old_name = current_item.getFileName()
            old_name = old_name[old_name.index('.')+1:old_name.rindex('.')]
            new_name = current_item.text(0)
            if old_name != new_name:
                if isinstance(current_item, GroupItem):
                    self.updateGroup(current_item)
                elif (
                    isinstance(current_item, ScriptItem)
                    or isinstance(current_item, GestureDesignItem)
                    or isinstance(current_item, HotkeyDesignItem)
                ):
                    updateItem(current_item)

    def updateAllDesigns(self, dirr, new_dir, old_dir):
        """
        updates all of the design files
        @dir:  directory to start searching from
        @new_dir:  New Path to add and replace old path with
        @old_dir:  Old path to look for/remove
        """
        old_dir = str(old_dir)
        new_dir = str(new_dir)

        for file in os.listdir(dirr):
            file_path = dirr + '/' + file
            if os.path.isdir(file_path) is True:
                return self.updateAllDesigns(
                    file_path,
                    new_dir,
                    old_dir
                )

            elif os.path.isfile(file_path):
                update_list = ['hotkey', 'gesture']
                if Locals().checkFileType(file_path) in update_list:
                    def checkFile(file_path):
                        current_file = open(file_path, 'r')
                        current_text = current_file.readlines()
                        current_file.close()
                        return current_text

                    current_text = checkFile(file_path)
                    if len(current_text) > 0:
                        text = current_text[0]
                        new_text = text.replace(old_dir, new_dir)
                        current_file = open(file_path, 'w')
                        current_file.write(new_text)
                        current_file.close()

    def updateAllButtons(self):
        """Updates the display of all of the buttons in  the Design Tab"""
        script_editor_widget = getWidgetAncestor(self, ScriptEditorWidget)
        design_tab = script_editor_widget.designTabWidget()
        design_tab.updateAllHotkeyDesigns()

    """ update global hotkeys registry"""
    """ $KATANA_RESOURCES/Scripts/hotkeys.json """

    def appendHotkeyToGlobalRegistry(self, item=None, hotkey=None):
        """
        Updates the hotkeys file located at
        $KATANA_RESOURCES/Scripts/hotkeys.json
        """
        file_path = self.filepath() + '/hotkeys.json'
        hotkey_dict = Locals().getFileDict(file_path)
        hotkey_dict[item.filepath()] = hotkey
        with open(file_path, 'w') as f:
            json.dump(hotkey_dict, f)

    def deleteHotkeyFromGlobalRegistry(self, item_path):
        """
        @item_path <str> path to script/design/etc
        removes the item path from the global hotkeys registry
        """
        def updateItemHotkeys():
            pass
        # reset item text
        design_items = self.getAllChildren(self.design_item)
        for item in design_items:
            if item.filepath() == item_path:
                item.setText(2, '')
        self.currentItem().setText(2, '')

        # delete from global file
        file_path = self.filepath() + '/hotkeys.json'
        hotkey_dict = Locals().getFileDict(file_path)
        hotkey_dict.pop(item_path, None)
        with open(file_path, 'w') as f:
            json.dump(hotkey_dict, f)

    def getInvertedHotkeyDict(self):
        """
        getInvertedHotkeyDict
        @return: <dict> of inverted global hotkey registry.
        This should then be used to get the file_path for
        a hotkey from the hotkey registered
        """
        inverted_hotkey_dict = {}
        file_path = self.filepath() + '/hotkeys.json'
        hotkey_dict = Locals().getFileDict(file_path)
        for file_path in list(hotkey_dict.keys()):
            hotkey = hotkey_dict[file_path]
            inverted_hotkey_dict[hotkey] = file_path

        return inverted_hotkey_dict

    def checkHotkeyExistance(self, hotkey):
        """
        @hotkey: <str> from QtGui.QKeySequence().toString
        checks to see if this hotkey already exists in the current
        master hotkey settings
        """
        hotkeys_dict = self.getInvertedHotkeyDict()
        if hotkey in list(hotkeys_dict.keys()):
            return True
        else:
            return False

    """ EVENTS """
    def contextMenuEvent(self, event, *args, **kwargs):
        def actionPicker(action):
            current_parent = self.currentItem()
            if (
                isinstance(current_parent, HotkeyDesignItem)
                or isinstance(current_parent, GestureDesignItem)
                or isinstance(current_parent, ScriptItem)
            ): # or isinstance(current_parent,HotkeyDesignMasterItem):
                current_parent = self.currentItem().parent()
            current_top_most_item = self.checkParentType(current_parent)

            # check to make sure its under designs/scripts,
            # if not send to top most level of appropriate category
            if action.text() == 'Create Hotkey Design':
                if isinstance(current_top_most_item, ScriptMasterItem):
                    current_parent = self.design_item
                self.createNewItem(current_parent, item_type='hotkey')
            elif action.text() == 'Create Gesture Design':
                if isinstance(current_top_most_item, ScriptMasterItem):
                    current_parent = self.design_item
                self.createNewItem(current_parent, item_type='gesture')
            elif action.text() == 'Create Script':
                if isinstance(current_top_most_item, HotkeyDesignMasterItem):
                    current_parent = self.scripts_item
                self.createNewItem(current_parent, 'script')
            elif action.text() == 'Create Group':
                self.createNewItem(current_parent, 'group')
            elif action.text() == 'Get File Path':
                print(self.currentItem().filepath())
        pos = event.globalPos()
        menu = QMenu(self)
        menu.addAction('Create Hotkey Design')
        menu.addAction('Create Gesture Design')
        menu.addAction('Create Script')
        menu.addAction('Create Group')
        menu.addAction('Get File Path')
        menu.popup(pos)
        action = menu.exec_(QCursor.pos())
        if action is not None:
            actionPicker(action)
        return QTreeWidget.contextMenuEvent(self, event, *args, **kwargs)

    def selectionChanged(self, event, *args, **kwargs):
        # =======================================================================
        # when the selection is changed, if its a script, it will load the script
        # into the code tab.
        #
        # This wont switch the tabs, as drag/drop is needed to set up the design 
        # layouts, so tab switching is handled through the mousePressEvent
        # =======================================================================
        script_editor_widget = getWidgetAncestor(self, ScriptEditorWidget)

        current_item = self.currentItem()

        if isinstance(current_item, ScriptItem):
            code_tab = script_editor_widget.designTabWidget().codeWidget()
            file_path = current_item.filepath()
            current_file = open('%s' % (file_path), 'r')
            text_list = current_file.readlines()
            text = ''.join(text_list)
            code_tab.setPlainText(text)
            current_file.close()
            script_editor_widget.setCurrentItem(current_item)
        return QTreeWidget.selectionChanged(self, event, *args, **kwargs)
    # all of these creates can be merged under one function that has a 'create type'

    def dragEnterEvent(self, *args, **kwargs):
        # =======================================================================
        # set up flags for drag/drop so that an item cannot be moved out
        # of its top most item
        # =======================================================================
        # create list of all children...
        current_top_most_item = self.checkParentType(self.currentItem())
        self.temp_list = []

        if isinstance(current_top_most_item, ScriptMasterItem):
            item_list = self.getAllChildren(self.design_item, child_list=[])
            self.design_item.setFlags(
                self.design_item.flags() ^ Qt.ItemIsDropEnabled
            )
            self.temp_list.append(self.design_item)
        elif isinstance(current_top_most_item, HotkeyDesignMasterItem):
            item_list = self.getAllChildren(self.scripts_item, child_list=[])
            self.scripts_item.setFlags(
                self.scripts_item.flags() ^ Qt.ItemIsDropEnabled
            )
            self.temp_list.append(self.scripts_item)

        for child in list(set(item_list)):
            if isinstance(child, GroupItem):
                self.temp_list.append(child)
                child.setFlags(child.flags() ^ Qt.ItemIsDropEnabled)

        return QTreeWidget.dragEnterEvent(self, *args, **kwargs)

    def dragLeaveEvent(self, *args, **kwargs):
        # =======================================================================
        # reset drag event flags
        # =======================================================================
        for child in self.temp_list:
                child.setFlags(child.flags() | Qt.ItemIsDropEnabled)
        # self.setDragDropMode(QAbstractItemView.NoDragDrop)
        return QTreeWidget.dragLeaveEvent(self, *args, **kwargs)

    def dropEvent(self, event, *args, **kwargs):
        # =======================================================================
        # reset drag/drop flags
        # =======================================================================
        for child in self.temp_list:
            child.setFlags(child.flags() | Qt.ItemIsDropEnabled)

        # =======================================================================
        # when an item is dropped, its directory is updated along with all
        # meta data relating to tabs/buttons/designs
        # =======================================================================
        # get attributes
        current_item = self.currentItem()
        old_parent = current_item.parent()

        return_val = super(ScriptTreeWidget, self ).dropEvent(event, *args, **kwargs)

        new_parent = current_item.parent()
        item_name = current_item.getFileName()

        old_file_dir = old_parent.filepath()
        if isinstance(old_parent, HotkeyDesignMasterItem):
            old_file_dir = old_parent.getFileDir()
        old_file_path = old_file_dir + '/' + item_name

        new_file_dir = new_parent.filepath()
        if isinstance(new_parent, HotkeyDesignMasterItem):
            new_file_dir = new_parent.getFileDir()
        new_file_path = new_file_dir + '/' + item_name

        # move file
        shutil.move(str(old_file_path), str(new_file_path))

        # update
        if isinstance(current_item, GroupItem):
            self.updateGroup(current_item, new_file_dir, old_file_dir)
        elif (
            isinstance(current_item, ScriptItem)
            or isinstance(current_item, GestureDesignItem)
            or isinstance(current_item, HotkeyDesignItem)
        ):
            self.updateItem(current_item, new_file_dir, old_file_dir)
            self.updateAllButtons()
            script_editor_widget = getWidgetAncestor(self, ScriptEditorWidget)
            script_editor_widget.designTabWidget().updateTabFilePath(new_file_path, old_file_path)
        return return_val

    def showTab(self, current_item):
        """sets the tab widget to the current item to be display"""
        script_editor_widget = getWidgetAncestor(self, ScriptEditorWidget)
        design_tab = script_editor_widget.designTabWidget()
        tab_bar = design_tab.tabBar()

        # Hotkey
        if (
            isinstance(current_item, HotkeyDesignItem)
            or isinstance(current_item, HotkeyDesignMasterItem)
        ):
            # create/show tab if it exists/doesnt
            for index in range(tab_bar.count()):
                widget = design_tab.widget(index)
                if hasattr(widget, 'getItem'):
                    if widget.getItem().getHash() == current_item.getHash():
                        design_tab.setCurrentWidget(widget)
                        return

            design_widget = HotkeyDesignEditorWidget(
                parent=design_tab,
                item=current_item,
                file_path=current_item.filepath()
            )
            design_widget.setHash(current_item.getHash())
            design_tab.addTab(design_widget, current_item.text(0))
            design_tab.setCurrentWidget(design_widget)

        # Script
        elif isinstance(current_item, ScriptItem):
            widget = design_tab.widget(0)
            design_tab.setCurrentWidget(widget)

        # Gesture
        elif isinstance(current_item, GestureDesignItem):
            for index in range(tab_bar.count()):
                widget = design_tab.widget(index)
                if hasattr(widget, 'getItem'):
                    if widget.getItem().getHash() == current_item.getHash():
                        design_tab.setCurrentWidget(widget)
                        return

            size = design_tab.getGestureWidgetSize()
            design_widget = GestureDesignEditorWidget(
                parent=design_tab,
                item=current_item,
                file_path=current_item.filepath(),
                script_list=self,
                size=size

            )
            design_widget.setHash(current_item.getHash())
            design_tab.addTab(design_widget, current_item.text(0))
            design_tab.setCurrentWidget(design_widget)

    def mouseReleaseEvent(self, event, *args, **kwargs):
        """on lmb change the design viewed tab/create a new tab"""
        current_item = self.itemAt(event.pos())
        if current_item:
            index = self.currentIndex()
            if event.button() == Qt.LeftButton:
                if index.column() != 2:
                    # display tab
                    self.setCurrentItem(current_item)
                    self.showTab(current_item)

            elif event.button() == Qt.MiddleButton:
                # drag / drop
                pass

        return QTreeWidget.mouseReleaseEvent(self,event,  *args, **kwargs)

    def deleteItem(self, item):
        if item:
            if isinstance(item, GroupItem):
                # has to recusively delete all children?
                for index in range(item.childCount()):
                    child = item.child(index)
                    self.deleteItem(child)

            else:
                script_editor_widget = getWidgetAncestor(self, ScriptEditorWidget)
                file_path = item.filepath()

                # delete disk location
                if os.path.exists(file_path):
                    os.remove(file_path)

                # del tab
                design_tab_widget = script_editor_widget.designTabWidget()
                tab_bar = design_tab_widget.tabBar()
                for index in range(tab_bar.count()):
                    widget = design_tab_widget.widget(index)
                    if (
                        isinstance(widget, HotkeyDesignEditorWidget)
                        or isinstance(widget, GestureDesignEditorWidget)
                    ):
                        if item.getHash() == widget.getHash():
                            design_tab_widget.removeTab(index)

                # needs to update all buttons again?
                self.updateAllButtons()
                self.updateAllDesigns(
                    script_editor_widget.filepath() + '/designs', '', file_path
                )
                # del item
                index = item.parent().indexOfChild(item)
                item.parent().takeChild(index)

                # del key
                del self.item_dict[str(item.getHash())]

    def keyPressEvent(self, event, *args, **kwargs):
        if self.accepts_inputs is True:
            if event.text() != '':
                # reset hotkey if user presses backspace/delete
                if(
                    event.key() == Qt.Key_Backspace
                    or event.key() == Qt.Key_Delete
                ):
                    inverted_hotkey_dict = self.getInvertedHotkeyDict()
                    hotkey = self.currentItem().text(2)
                    item_path = inverted_hotkey_dict[hotkey]
                    self.deleteHotkeyFromGlobalRegistry(item_path)
                    return QTreeWidget.keyPressEvent(self, event, *args, **kwargs)

                # get modifiers, not sure if I'm still using this...
                self.shift = bool(event.modifiers() & Qt.ShiftModifier)
                self.control = bool(event.modifiers() & Qt.ControlModifier)
                self.alt = bool(event.modifiers() & Qt.AltModifier)

                # get key sequence
                hotkey = QKeySequence(
                    int(event.modifiers()) + event.key()
                ).toString()

                # check existance of hotkey, and append the keypath to the
                # global hotkey registry
                hotkey_exists = self.checkHotkeyExistance(hotkey)
                if hotkey_exists is True:
                    # create pop up box
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText(
                        "The hotkey \' %s \' exists.  Would you like to override it and continue?" % hotkey
                    )
                    msg.setWindowTitle('omg its a duplicate')
                    msg.setStandardButtons(
                        QMessageBox.Ok | QMessageBox.Cancel
                    )
                    retval = msg.exec_()

                    # if user accepts input
                    if retval == 1024:
                        inverted_hotkey_dict = self.getInvertedHotkeyDict()
                        item_path = inverted_hotkey_dict[hotkey]
                        self.deleteHotkeyFromGlobalRegistry(item_path)
                        self.currentItem().setText(2, hotkey)
                        self.appendHotkeyToGlobalRegistry(item=self.currentItem(), hotkey=hotkey)
                else:
                    self.currentItem().setText(2, hotkey)
                    self.appendHotkeyToGlobalRegistry(item=self.currentItem(), hotkey=hotkey)

        else:
            if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
                # ===================================================================
                # if enter pressed show warning box
                # ===================================================================
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Are ya sure matey!?!?? (said like a pirate)")
                msg.setStandardButtons(
                    QMessageBox.Ok | QMessageBox.Cancel
                )
                retval = msg.exec_()
                # ===================================================================
                # if user selects ok on warning box
                # ===================================================================
                if retval == 1024:
                    item = self.currentItem()
                    self.deleteItem(item)
                    if isinstance(item, GroupItem):
                        # os.rmdir(item.filepath())
                        shutil.rmtree(item.filepath())
                        # os.system("rm -rf %s" % build_dir)
                        index = item.parent().indexOfChild(item)
                        item.parent().takeChild(index)

        return QTreeWidget.keyPressEvent(self, event, *args, **kwargs)

    def keyReleaseEvent(self, *args, **kwargs):
        #self.accepts_inputs = False
        return QTreeWidget.keyReleaseEvent(self, *args, **kwargs)


""" ITEMS """
class DataTypeDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(DataTypeDelegate, self).__init__(parent)
        # self.katana_main = UI4.App.ScriptEditorWidget.GetScriptEditor()
        #self.katana_main.removeEventFilter(self.katana_main.event_filter_widget)

    """ Do I need this"""
    def sizeHint(self, *args, **kwargs):
        return QItemDelegate.sizeHint(self, *args, **kwargs)

    """ Do I need this"""
    def updateEditorGeometry(self, *args, **kwargs):
        return QItemDelegate.updateEditorGeometry(self, *args, **kwargs)

    def createEditor(self, parent, option, index):
        if index.column() == 2:
            current_item = self.parent().currentItem()
            if current_item.getItemType() != 'group':
                self.parent().accepts_inputs = True
                delegate_widget = QLabel(parent)
                delegate_widget.setStyleSheet(
                    'background-color: rgb(240, 200, 0);\
                    color: rgb(15, 55, 255)'
                )
                return delegate_widget
        else:
            return QItemDelegate.createEditor(self, parent, option, index)

    def closeEditor(self, *args, **kwargs):
        print('close')
        self.parent().accepts_inputs = False
        return QItemDelegate.closeEditor(self, *args, **kwargs)

    """ Do I need these? """
    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.DisplayRole)
        editor.setText(text)
        #editor.setText('')
        #self.closeEditor()
        return QItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        """
        # swap out 'v' for current value
        """
        # =======================================================================
        # get data
        # =======================================================================
        self.parent().accepts_inputs = False
        new_value = editor.text()
        if new_value == '':
            return
        model.setData(index, QVariant(new_value))


class BaseItem(QTreeWidgetItem):
    """
    Abstract item to be inherited and used as the starting point
    for all of the different types of items available for hte user
    in the tree view
    """
    def __init__(
        self,
        parent=None,
        text='BaseItem',
        unique_hash=None
    ):
        super(BaseItem, self).__init__(parent)
        script_editor_widget = getWidgetAncestor(self.treeWidget(), ScriptEditorWidget)
        self.hash_list = self.getHashList(script_editor_widget.filepath())

    def initialize(
        self,
        parent=None,
        text='group',
        unique_hash=None,
        file_dir=None
    ):
        """
        initialize the default attributes for each item
        @parent: <BaseItem>
        @text: <str> display name
        @unique_hash: <str> unique hash
        @file_dir: <str> directory of file
        """
        def getFileName(unique_hash, text):
            file_name = '%s.%s' % (unique_hash, text)
            if self.getItemType() == 'script':
                file_name += '.py'
            elif self.getItemType() == 'hotkey':
                file_name += '.json'
            return file_name

        # =======================================================================
        # set meta data
        # =======================================================================
        self.setFileDir(file_dir)

        # check hash
        if not unique_hash:
            unique_hash = self.createHash(text, self.getFileDir())
            file_name = getFileName(unique_hash, text)
            self.setFileName(file_name)
            self.setFilepath(self.getFileDir() + '/' + self.getFileName())
            # why am I creating a dir here? for everything?
            self.createData(self.filepath())
        # set up item meta data
        file_name = getFileName(unique_hash, text)
        self.setFileName(file_name)
        self.setFilepath(self.getFileDir() + '/' + self.getFileName())
        self.setHash(unique_hash)

        # set display text
        self.setText(0, str(text))

        # create bits (file / directory)

    """  PROPERTIES """

    def getItemType(self):
        return self.item_type

    def setItemType(self, item_type):
        self.setText(1, item_type)
        self.item_type = item_type

    def getFileName(self):
        return self.file_name

    def setFileName(self, file_name):
        self.file_name = file_name

    def getFileDir(self):
        return self.file_dir

    def setFileDir(self, file_dir):
        self.file_dir = file_dir

    """
    def createFile(self, file_path):
        current_file = open(file_path, 'w')
        current_file.write('')
        current_file.close()
    """

    def getHashList(self, location, hash_list=[]):
        for child in os.listdir(location):
            child_location = '%s/%s' % (location, child)
            if '.' in child:
                unique_hash = child.split('.')[0]
                hash_list.append(unique_hash)

            if os.path.isdir(child_location):
                self.getHashList(child_location, hash_list=hash_list)
        return list(set(hash_list))

    def createHash(self, thash, location):
        thash = int(math.fabs(hash(str(thash))))
        if str(thash) in self.hash_list:
            thash = int(math.fabs(hash(str(thash))))
            return self.createHash(str(thash), location)
        return thash

    def setHash(self, unique_hash):
        self.hash = unique_hash

    def getHash(self):
        return str(self.hash)

    def setFilepath(self, file_path):
        self._file_path = file_path

    def filepath(self):
        return self._file_path


class GroupItem(BaseItem):
    def __init__(
        self,
        parent=None,
        text='group',
        unique_hash=None,
        file_dir=None
    ):
        super(GroupItem, self).__init__(parent)

        self.setFlags(self.flags() | Qt.ItemIsEditable)

        self.setItemType('group')

        self.initialize(
            parent=parent,
            text=text,
            unique_hash=unique_hash,
            file_dir=file_dir
        )

    def createData(self, directory):
        if not os.path.exists(directory):
            os.mkdir(directory)


class ScriptMasterItem(BaseItem):
    def __init__(
        self,
        parent=None,
        filepath="",
        text='Script',
        unique_hash=None
    ):
        super(ScriptMasterItem, self).__init__(parent)
        self.setFlags(
            self.flags()
            & ~Qt.ItemIsEditable
            & ~Qt.ItemIsDragEnabled
        )
        self.setFileDir(filepath + '/scripts')
        self.setFilepath(filepath + '/scripts')
        self.setText(0, text)
        self.setHash(unique_hash)
        self.setItemType('master')


class ScriptItem(BaseItem):
    def __init__(
            self,
            parent=None,
            text='Script',
            unique_hash=None,
            file_dir=None
    ):

        super(ScriptItem, self).__init__(parent)
        self.setFlags(
            self.flags()
            & ~Qt.ItemIsDropEnabled
            | Qt.ItemIsDragEnabled
            | Qt.ItemIsEditable
        )

        self.setItemType('script')

        self.initialize(
                parent=parent,
                text=text,
                unique_hash=unique_hash,
                file_dir=file_dir
        )

    def createData(self, file_path):
        current_file = open(file_path, 'w')
        current_file.write('')
        current_file.close()


class HotkeyDesignBaseItem(BaseItem):
    def __init__(
        self,
        parent=None,
        text='hotkey',
        unique_hash=None
    ):
        super(HotkeyDesignBaseItem, self).__init__(parent)
        self.setItemType('hotkey')

    def createData(self, file_path):
        """
        Creates the hotkey design file as a JSON
        @file_path <str> path to file
        """
        """
        current_file = open(file_path, 'w')
        # copy/paste from design tab
        button_list = [
            '1', '2', '3', '4',
            'q', 'w', 'e', 'r',
            'a', 's', 'd', 'f',
            'z', 'x', 'c', 'v',
        ]
        current_file.write(r'=|'.join(button_list) + '=')
        current_file.close()
        """
        hotkeys = '1234qwerasdfzxcv'
        hotkey_dict = {}
        for letter in hotkeys:
            hotkey_dict[letter] = ''
        if file_path:
            # Writing JSON data
            with open(file_path, 'w') as f:
                json.dump(hotkey_dict, f)


class HotkeyDesignMasterItem(HotkeyDesignBaseItem):
    def __init__(self, parent=None, filepath="", text='HotkeyDesign', unique_hash='master'):
        super(HotkeyDesignMasterItem, self).__init__(parent)
        self.setFlags(
            self.flags()
            & ~Qt.ItemIsEditable
            & ~Qt.ItemIsDragEnabled
        )

        self.setFileDir(filepath + '/designs')
        self.setFileName('master.json')
        self.setFilepath(self.getFileDir() + '/' + self.getFileName())

        if not os.path.exists(self.filepath()):
            self.createData(self.filepath())

        self.setHash(unique_hash)
        self.setText(0, str(text))
        #self.setText(2, unique_hash)


class HotkeyDesignItem(HotkeyDesignBaseItem):
    def __init__(
        self,
        parent=None,
        text='HotkeyDesign',
        unique_hash=None,
        file_dir=None
    ):
        super(HotkeyDesignItem, self).__init__(parent)
        self.setFlags(
            self.flags()
            & ~Qt.ItemIsDropEnabled
            | Qt.ItemIsDragEnabled
            | Qt.ItemIsEditable
        )

        self.initialize(
            parent=parent,
            text=text,
            unique_hash=unique_hash,
            file_dir=file_dir
        )

        self.setItemType('hotkey')


class GestureDesignItem(HotkeyDesignBaseItem):
    def __init__(
        self,
        parent=None,
        text='GestureDesign',
        unique_hash=None,
        file_dir=None
    ):
        super(GestureDesignItem, self).__init__(parent)
        self.setFlags(
            self.flags()
            & ~Qt.ItemIsDropEnabled
            | Qt.ItemIsDragEnabled
            | Qt.ItemIsEditable
        )

        self.initialize(
            parent=parent,
            text=text,
            unique_hash=unique_hash,
            file_dir=file_dir
        )

        self.setItemType('gesture')

    def createData(self, file_path):
        """
        Creates the hotkey design file as a JSON
        @file_path <str> path to file
        """
        hotkeys = '01234567'
        hotkey_dict = {}
        for letter in hotkeys:
            hotkey_dict[letter] = ''
        if file_path:
            # Writing JSON data
            with open(file_path, 'w') as f:
                json.dump(hotkey_dict, f)


class DesignTab(QTabWidget):
    """Tab on right where the user does most of the editing

    Args:
        python_editor (QWidget): which should be used as the Python Editor
            note that this will need to have its "codeWidget" overwritten to
            return a QPlainTextEditWidget
        """
    def __init__(self, parent=None, python_editor=AbstractPythonEditor):
        super(DesignTab, self).__init__(parent)
        self.setAcceptDrops(True)

        self._python_editor_widget = python_editor()
        self.addTab(self._python_editor_widget, 'Python')

    def __name__(self):
        return '__main_tab__'

    def setPythonEditor(self, editor_widget):
        self._python_editor_widget = editor_widget

    def codeWidget(self):
        return self.pythonEditorWidget().codeWidget()

    def pythonEditorWidget(self):
        return self._python_editor_widget

    """ UTILS """
    def updateTabFilePath(self, new_file_path, old_file_path):
        """

        Args:
            new_file_path (str): after the file path has been changed, this is
                the path to the new one on disk.  Right now this is being used with
                "def groupRename".
            old_file_path (str)
        """
        design_tab = self
        tab_bar = design_tab.tabBar()
        for index in range(tab_bar.count()):
            widget = design_tab.widget(index)
            if hasattr(widget, 'file_path'):
                if old_file_path in widget.filepath():
                    file_path = widget.filepath().replace(old_file_path, new_file_path)
                    widget.setFilepath(file_path)

    """ HOTKEYS """
    def updateAllHotkeyDesigns(self):
        tab_bar = self.tabBar()
        for index in range(tab_bar.count()):
            widget = self.widget(index)
            if (
                isinstance(widget, HotkeyDesignEditorWidget)
                or isinstance(widget, GestureDesignEditorWidget)
            ):
                widget.updateButtons()

    """ GESTURES """
    def getGestureWidgetSize(self):
        """Gets the height of the Gesture Widget, with offsetsfrom child widgets"""
        height = self.height()
        parent_layout = self.parent().layout()

        for index in range(1, parent_layout.count()):
            child = parent_layout.itemAt(index).widget()
            height -= child.geometry().height()
            #height -= parent_layout.spacing()
        size = min(
            self.width(), height
        )
        return size

    def updateAllGestureDesignsGeometry(self):
        design_tab = self
        tab_bar = design_tab.tabBar()
        for index in range(tab_bar.count()):
            widget = design_tab.widget(index)
            if isinstance(widget, GestureDesignEditorWidget):
                size = self.getGestureWidgetSize()
                widget.updatePolygons(size=size)

    """ EVENTS """
    def mousePressEvent(self, event, *args, **kwargs):
        tab_bar = self.tabBar()
        current_tab = tab_bar.tabAt(event.pos())
        if current_tab > 0:
            self.removeTab(tab_bar.tabAt(event.pos()))

        return QTabWidget.mousePressEvent(self, event, *args, **kwargs)

    def resizeEvent(self, event, *args, **kwargs):
        self.updateAllGestureDesignsGeometry()
        return QTabWidget.resizeEvent(self, event, *args, **kwargs)



#
# class PythonWidget(QWidget):
#     def __init__(self, parent=None):
#         super(PythonWidget, self).__init__(parent)
#
#         layout = QVBoxLayout(self)
#         python_tab = UI4.App.Tabs.CreateTab('Python', None)
#
#         layout.addWidget(python_tab)
#
#         widget = python_tab.getWidget()
#         python_widget = widget._pythonWidget
#         script_widget = python_widget._FullInteractivePython__scriptWidget
#         self.command_widget = script_widget.commandWidget()
#
#     def getCommandWidget(self):
#         return self.command_widget


if __name__ == '__main__':
    import sys
    from qtpy.QtWidgets import QApplication
    from cgwidgets.utils import centerWidgetOnScreen
    app = QApplication(sys.argv)
    main_widget = ScriptEditorWidget()

    main_widget.show()
    centerWidgetOnScreen(main_widget)
    sys.exit(app.exec_())
    main()

