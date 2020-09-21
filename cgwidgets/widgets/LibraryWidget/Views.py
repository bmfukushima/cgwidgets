"""
Detailed:
    # required...
    - Text Edit fields need to be changed... so users can't break them...
    - break out multi dir populater...
    - sorting...
    # would be nice...
    - Sliders in between
        QSplitterHandle?

List:
    one long list? Like really freaking long?

"""
from collections import OrderedDict
import json
import math
import os
import re
import sys

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *

from .__utils__ import iUtils
from cgwidgets import utils as gUtils


class ImageListModel(QAbstractTableModel):
    """
    [ row(columns), row(columns), row(columns) ]
    @selection_list: < list > of < ImageWidgets > that are currently selected
        by the user.

        Should this change to updating the row data?

        This is causing issues... when having multiple views in displaying what
        is/is not selected...

        When you update the mode... it will not honor this, as it cannot read
        the ImageWidgets data to confirm if it is selected or not...  As the image
        widgets data is only valid for that specific view...

        How do you sync this?

    @imageJSONList: < list> of < JSON >
        This is the row list of data that is shown to the user...
    @metadata: <dict> of <list>
        metadata['hidden'] = [filepath, filepath]
        metadata['selection'] = [filepath, filepath]
        Need something here to hold the metadata for
            selection
            hidden
            etc
    """
    def __init__(self, parent_widget=None, filedirs_list=[]):
        super(ImageListModel, self).__init__()
        # self.selection_list = []
        self.key_map = {
            0: 'name',
            1: 'type',
            2: 'notes',
            3: 'data',
            4: 'frame',
            5: 'proxy',
            6: 'filepath'
            }
        self._metadata = {}
        self.metadata['hidden'] = []
        self.metadata['selected'] = []
        self._parent_widget = parent_widget

        try:
            self.populateModelFromDirectory(filedirs_list)
        except TypeError:
            # this will auto fail if the filedirs_list is not provided...
            # this is used to bypass and set the model later if needed
            pass

    def columnCount(self, parent=None):
        return len(self.key_map)

    def rowCount(self, parent=None):
        return len(self.imageJSONList)



    """ UTILS """

    def populateModelFromDirectory(self, filedirs_list):
        """
        populates all of the items in the model from a model
        specified on disk
        @filedir: <str> path to directory
        """
        # combine directories together
        items = []
        for filedir in filedirs_list:
            items += ['/'.join([filedir, filename]) for filename in os.listdir(filedir)]

        # check data, if good add it to the row list
        row_list = []
        for filepath in items:
            try:
                with open(filepath, 'r') as f:
                    jsondata = json.load(f)
            except IOError:
                pass
            except ValueError:
                pass
            else:
                jsondata['filepath'] = filepath
                row_list.append(jsondata)

        self.imageJSONList = row_list

    def populateModelFromList(self, json_list):
        """
        @row_list: <list> of json file paths
        """
        # check data, if good add it to the row list
        row_list = []
        for filepath in json_list:
            try:
                with open(filepath, 'r') as f:
                    jsondata = json.load(f)
            except IOError:
                pass
            except ValueError:
                pass
            else:
                jsondata['filepath'] = filepath
                row_list.append(jsondata)

        self.imageJSONList = row_list

    def appendToSelectionList(self, path):
        try:
            self.metadata['selected'].remove(path)
        except:
            pass
        finally:
            self.metadata['selected'].append(path)

    def removeFromSelectionList(self, path):
        try:
            self.metadata['selected'].remove(path)
        except ValueError:
            pass

    def populateHideList(self, user_search_text):
        """
        @user_search_text: < str >
            string input from the user in the search bar widget
            this should be in the format of
                jsonkey{regex, regex, regex}
                ie
                    name{.*}
        """
        # reset hidden list
        self.metadata['hidden'] = []
        # get search text list...
        search_param_list = user_search_text.replace(' ','').split('}')[:-1]

        # check for null cases to reset
        if (
            user_search_text.replace(' ', '') == ''
            or len(search_param_list) == 0
        ):
            return
        # temp list
        hide_list = []

        # run through list and check for matches in json files
        for jsondata in self.imageJSONList:
            hide_list.append(jsondata['filepath'])
            for search_param in search_param_list:
                # test{} blahhaha{} akdlsjf{}
                # test{asdf,asdf,asdf}
                try:
                    # split data into key and regex
                    user_search_key, user_regex = search_param.split('{')
                    # check to make sure the key exists
                    key_data = jsondata[user_search_key]

                    # get the user regex for this specific key
                    for regex in user_regex.split(','):
                        if re.search(regex, key_data):
                            try:
                                hide_list.remove(jsondata['filepath'])
                            except ValueError:
                                """
                                bypass incase this gets multiple
                                hits from the regex list
                                """
                                pass
                except KeyError:
                    print('{key} does not exist in {file}'.format(
                        key=user_search_key,
                        file=jsondata['filepath'])
                    )

        self.metadata['hidden'] = hide_list

    def updateViews(self):
        """
        Updates all of the views, this is not attached to this model
        in any way... so I could probably just send this to a iUtils...
        """
        main_widget = gUtils.getMainWidget(self._parent_widget, 'Library')

        detailed_view = main_widget.detailed_view
        thumbnail_view = main_widget.thumbnail_view
        list_view = main_widget.list_view
        views = [detailed_view, thumbnail_view, list_view]

        for view in views:
            view.update()

    """ PROPERTIES """

    @property
    def parent_widget(self):
        return self._parent_widget

    @parent_widget.setter
    def parent_widget(self, parent_widget):
        self._parent_widget = parent_widget

    @property
    def image_size(self):
        return self._image_size

    @image_size.setter
    def image_size(self, image_size):
        self._image_size = image_size

    @property
    def imageJSONList(self):
        return self._imageJSONList

    @imageJSONList.setter
    def imageJSONList(self, jsondata):
        self._imageJSONList = jsondata

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        self._metadata = metadata


class ThumbnailViewWidget(QScrollArea):
    """
    primary layout of the contact sheet
    """
    def __init__(self, parent=None):
        super(ThumbnailViewWidget, self).__init__(parent)
        self.top_level_widget = QWidget()
        self.setWidget(self.top_level_widget)

        self.main_layout = QGridLayout()
        self.top_level_widget.setLayout(self.main_layout)

        # global attributues
        self._image_size = 100
        self._spacing = 15
        self._num_columns = 0

        # size policies
        self.setWidgetResizable(True)

        self.main_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(self.spacing)
        self.top_level_widget.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed
        )
        """
        self.setMinimumHeight(1)

        self.top_level_widget.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding
        )
        """
    """ PROPERTIES """
    @property
    def spacing(self):
        return self._spacing

    @spacing.setter
    def spacing(self, spacing):
        self._spacing = spacing

    @property
    def num_columns(self):
        return self._num_columns

    @num_columns.setter
    def num_columns(self, num_columns):
        self._num_columns = num_columns

    @property
    def image_size(self):
        return self._image_size

    @image_size.setter
    def image_size(self, image_size):
        self._image_size = image_size

    @property
    def widget_list(self):
        return self._widget_list

    @widget_list.setter
    def widget_list(self, widget_list):
        self._widget_list = widget_list

    """ FUNCTIONS """

    def setModel(self, model):
        self.model = model
        # reset
        # self.resetHeaderWidgetLists()
        gUtils.clearLayout(self.main_layout)

        # populate model
        widget_list = []
        old_selection_list = []
        new_selection_list = []
        for row in range(model.rowCount()):
            jsondata = model.imageJSONList[row]
            if jsondata['filepath'] not in self.model.metadata['hidden']:
                thumbnail_view_item = ThumbnailViewItem(
                    parent=self,
                    name=jsondata['name'],
                    image_size=self.image_size,
                    jsondata=jsondata
                )
                # thumbnail_view_widget.setStyleSheet("background-color: rgb(255,255,255)")
                widget_list.append(thumbnail_view_item)
    
                if jsondata in old_selection_list:
                    image_widget = thumbnail_view_item.image_widget
    
                    new_selection_list.append(image_widget)
                    image_widget.setSelected()

        self.widget_list = widget_list
        self.layoutWidgets()

        """
        try:
            self.model.metadata['selected'] = new_selection_list
        except AttributeError:
            # running in IDE mode
            pass
        """

    def getNumColumns(self):
        """
        @return: <int> number of columns based off of the
            size of the image
        """
        # get attributes
        image_size = self.image_size
        w = self.geometry().width() - 50
        
        border_width = iUtils.getSetting('IMAGE_SELECTED_BORDER_WIDTH')
        # compensate for scroll bar
        if self.verticalScrollBar().isVisible() is True:
            scroll_bar_width = self.verticalScrollBar().width()
            min_width = image_size + scroll_bar_width
            total_width = w - scroll_bar_width
        else:
            min_width = image_size
            total_width = w

        # do math to get number of columns
        total_width += (self.spacing * 2) - (border_width*2)
        total_image_size = image_size + self.spacing + border_width
        num_columns = math.trunc( total_width / total_image_size )

        # if widget is so small that there are no columns, return
        if num_columns < 1:
            num_columns = 1
        self.setMinimumWidth(min_width)
        return num_columns

    def layoutWidgets(self, num_columns=None):
        # get num columns
        if not num_columns:
            num_columns = self.getNumColumns()
            self.num_columns = num_columns

        # clear layout
        gUtils.clearLayout(self.main_layout)

        # populate layout
        if hasattr(self, 'widget_list'):
            for index, widget in enumerate(self.widget_list):
                self.main_layout.addWidget(
                    widget,
                    int(index / num_columns),
                    index % num_columns
                )

    def update(self):
        self.image_size = gUtils.getMainWidget(self, 'Library').image_size
        # update model
        try:
            self.setModel(self.model)
        except AttributeError:
            pass

        # update selected items...
        for widget in self.widget_list:
            if widget.image_widget.isSelected():
                widget.image_widget.setSelected()
            else:
                widget.image_widget.setUnselected()

    """ EVENTS """

    def resizeEvent(self, event, *args, **kwargs):
        self.layoutWidgets()
        return QScrollArea.resizeEvent(self, event, *args, **kwargs)


class ThumbnailViewItem(QWidget):
    """
    Thumbnail Item for the ThumbnailView
    @json: <dict> json file data
    """
    def __init__(
            self,
            parent=None,
            name=None,
            image_size=None,
            jsondata=None
        ):
        super(ThumbnailViewItem, self).__init__(parent)
        self.json = jsondata
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

        self.image_widget, self.pixmap = iUtils.createImageWidget(
            self,
            self.json,
            image_size
        )

        vbox.addWidget(self.image_widget)
        # Create Label

        self.label = QLabel(name)
        self.label.setFixedWidth(image_size)
        vbox.addWidget(self.label)

    """ PROPERTIES """
    @property
    def json(self):
        return self._json

    @json.setter
    def json(self, json):
        self._json = json

    @property
    def pixmap(self):
        return self._pixmap

    @pixmap.setter
    def pixmap(self, pixmap):
        self._pixmap = pixmap

    @property
    def image_widget(self):
        return self._image_widget

    @image_widget.setter
    def image_widget(self, image_widget):
        self._image_widget = image_widget


class DetailedViewWidget(QWidget):
    """
    @header_height < int > height of the horizontal header
        spacer | hheader
    @column_spacing < int > white space between columns
        hheader.splitter | <DetailedViewItem>
    @row_spacing < int > white space between rows
    @row_height < int > height of rows
    @column_width < int > width of columns
    """
    def __init__(self, parent=None, model=None):
        super(DetailedViewWidget, self).__init__(parent)

        self.setStyleSheet("""
        border-width: 0px;
        border: None;
        margin: 0px;
        padding: 0px;
        """)
        # global attrs
        self.key_map = [
            'name',
            'type',
            'notes',
            'data',
            'frame',
            'proxy',
            'filepath'
            ]
        self._row_spacing = 15
        self._row_height = 100
        self._column_width = 100
        self._column_spacing = 5
        self._header_height = 40

        # main layout
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        # create widgets
        self.hscrollbar = QScrollBar(Qt.Horizontal)
        self.vscrollbar = QScrollBar(Qt.Vertical)

        self.hheader = DetailedViewHorizontalHeader(self, hscrollbar=self.hscrollbar)
        self.vheader = DetailedViewVerticalHeader(self, vscrollbar=self.vscrollbar)
        self.main_table = DetailedViewTable(self, hscrollbar=self.hscrollbar, vscrollbar=self.vscrollbar)

        # set widget sizes
        main_widget = gUtils.getMainWidget(self, 'Library')
        self.main_layout.setSpacing(main_widget.main_splitter_handle_width)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # add widgets to layout
        self.main_vlayout = QVBoxLayout()
        self.main_vlayout.addWidget(self.hheader)
        self.main_vlayout.addWidget(self.main_table)
        self.main_layout.addWidget(self.vheader)
        self.main_layout.addLayout(self.main_vlayout)

    def resetHeaderWidgetLists(self):
        """
        Each horizontal header item has a list of all of the
        widgets that are in that column.  This list is used
        for column based operations.

        This function clears that list
        """
        header_items = self.hheader.getHeaderItems()
        for key in list(header_items.keys()):
            widget = header_items[key]
            widget.resetWidgetList()

    def setModel(self, model):
        """
        sets the model
        """
        self.model = model

        # reset
        self.resetHeaderWidgetLists()
        gUtils.clearLayout(self.main_table.main_layout)

        # update view
        for row in range(model.rowCount()):
            jsondata = model.imageJSONList[row]
            jsondata = model.imageJSONList[row]
            if jsondata['filepath'] not in self.model.metadata['hidden']:
                item = DetailedViewItem(self, jsondata=jsondata)
                item.setFixedHeight(self.row_height)
                self.main_table.main_layout.addWidget(item)

        self.hheader.updateColumnsWidth()
        self.vheader.update()

    def update(self):
        # self.image_size = gUtils.getMainWidget(self, 'Library').image_size
        self.row_height = gUtils.getMainWidget(self, 'Library').image_size
        # update model
        try:
            self.setModel(self.model)
        except AttributeError:
            # model will not exist on init
            pass

        # update selected items...
        layout = self.vheader.main_layout
        for index in range(layout.count()):
            widget = layout.itemAt(index).widget()
            if widget.isSelected():
                widget.setSelected()
            else:
                widget.setUnselected()

    """  PROPERTIES """

    @property
    def header_height(self):
        return self._header_height

    @header_height.setter
    def header_height(self, header_height):
        self._header_height = header_height

        # update widgets
        self.vheader.spacer.setFixedHeight(header_height)
        self.hheader.setFixedHeight(header_height)

    @property
    def column_spacing(self):
        return self._column_spacing

    @column_spacing.setter
    def column_spacing(self, column_spacing):
        self._column_spacing = column_spacing
        self.hheader.splitter.setHandleWidth(column_spacing)

        table_layout = self.main_table.main_layout()
        for row in range(len(table_layout.count())):
            widget = table_layout.itemAt(row).widget()
            layout = widget.layout()
            layout.setSpacing(column_spacing)

    @property
    def row_spacing(self):
        return self._row_spacing

    @row_spacing.setter
    def row_spacing(self, row_spacing):
        self._row_spacing = row_spacing

        # update widgets
        self.main_table.main_layout.setSpacing(row_spacing)

        border_width = iUtils.getSetting('IMAGE_SELECTED_BORDER_WIDTH')
        # self.vheader.main_layout.setSpacing(row_spacing + (border_width * 2))
        self.vheader.main_layout.setSpacing(row_spacing)

    @property
    def row_height(self):
        return self._row_height

    @row_height.setter
    def row_height(self, row_height):
        """
        sets the row height and updates the widgets...
        should probably break this into an update
        method as well...
        """
        self._row_height = row_height

        # update row heights
        for i in range(self.main_table.main_layout.count()):
            widget = self.main_table.main_layout.itemAt(i).widget()
            widget.setFixedHeight(row_height)
        
        self.vheader.update()

    @property
    def column_width(self):
        return self._column_width

    @column_width.setter
    def column_width(self, column_width):
        self._column_width = column_width


class DetailedViewTable(QScrollArea):
    """
    Directory folder viewed as a detailed view.  This a display option
    for the user that is changed by the "mode" drop down.
    """
    def __init__(self, parent=None, hscrollbar=None, vscrollbar=None):
        super(DetailedViewTable, self).__init__(parent)
        self.setStyleSheet("border:None")
        # attrs
        self.item_list = []

        # setup layout
        self.setupMainLayout()
        self.setHorizontalScrollBar(hscrollbar)
        self.setVerticalScrollBar(vscrollbar)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def setupMainLayout(self):
        """
        Sets up the main layout for the entire widget
        """
        # set up top level layout/widget
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        self.setWidget(self.main_widget)

        # set up policies
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(self.parent().row_spacing)
        self.main_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setWidgetResizable(True)
        self.setMinimumWidth(1)

        self.main_widget.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed
        )

    def resizeEvent(self, *args, **kwargs):
        self.parent().hheader.updateColumnsWidth()
        return QScrollArea.resizeEvent(self, *args, **kwargs)


class DetailedViewVerticalHeader(QWidget):
    """
    @header_items: <dict> of widget
        header_items[key] = widget
    """
    def __init__(self, parent=None, vscrollbar=None):
        super(DetailedViewVerticalHeader, self).__init__(parent)
        # setup widgets
        self.main_scrollarea = QScrollArea()
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()

        # set up attr
        self.main_scrollarea.setVerticalScrollBar(vscrollbar)
        self.main_scrollarea.setWidgetResizable(True)
        self.main_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.main_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # set up proxy layout (top level)
        proxy_layout = QVBoxLayout()

        self.setLayout(proxy_layout)
        self.spacer = QLabel()
        self.spacer.setFixedHeight(
            self.parent().header_height
            + self.parent().row_spacing
            - (iUtils.getSetting('IMAGE_SELECTED_BORDER_WIDTH') * 2)
        )
        # set up main layout

        self.main_widget.setLayout(self.main_layout)
        self.main_scrollarea.setWidget(self.main_widget)

        # add widgets to proxy layout
        proxy_layout.addWidget(self.spacer)
        proxy_layout.addWidget(self.main_scrollarea)

        # set up policies
        proxy_layout.setAlignment(Qt.AlignTop)
        proxy_layout.setContentsMargins(0, 0, 0, 0)
        proxy_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        border_width = iUtils.getSetting('IMAGE_SELECTED_BORDER_WIDTH')
        self.main_layout.setSpacing(self.parent().row_spacing + (border_width * 2))
        self.main_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        #self.setStyleSheet("border:None; background-color: rgb(0,255,0)")
        self.main_widget.setStyleSheet("border:None")
        self.main_scrollarea.setStyleSheet("border:None")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)

    def getRowHeight(self):
        try:
            row_height = self.parent().row_height
        except AttributeError:
            row_height = self.parent().parent().parent().row_height
        return row_height

    @property
    def pixmap(self):
        return self._pixmap

    @pixmap.setter
    def pixmap(self, pixmap):
        self._pixmap = pixmap

    def update(self):
        """
        updates the row height
        """
        gUtils.clearLayout(self.main_layout)
        self.populate()

        row_height = self.getRowHeight() + (iUtils.getSetting('IMAGE_SELECTED_BORDER_WIDTH') * 2)
        self.setFixedWidth(row_height)

    def populate(self):

        model = self.parent().model
        for row in range(model.rowCount()):
            jsondata = model.imageJSONList[row]
            if jsondata['filepath'] not in model.metadata['hidden']:
                image_widget, self.pixmap = iUtils.createImageWidget(
                    self, jsondata, self.getRowHeight()
                )
                #image_widget.setFixedWidth(self.getRowHeight())
                self.main_layout.addWidget(image_widget)
        return


class DetailedViewHorizontalHeader(QScrollArea):
    """
    @header_items: <dict> of widget
        header_items[key] = widget
    """
    def __init__(self, parent=None, hscrollbar=None):
        super(DetailedViewHorizontalHeader, self).__init__(parent)
        self.setStyleSheet("border:None")
        # global attrs
        self.resetHeaderItems()
        self.setHorizontalScrollBar(hscrollbar)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # main widget
        self.splitter = QSplitter()
        self.splitter.setHandleWidth(self.parent().column_spacing)
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.splitterMoved.connect(self.updateColumnsWidth)
        self.setWidget(self.splitter)
        self.splitter.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Fixed
        )

        # create header items
        for column_name in self.parent().key_map:
            label = DetailedViewHorizontalHeaderItem(parent=self, text=column_name)
            label.resize(self.parent().column_width, label.height())
            self.splitter.addWidget(label)
            self.setHeaderItems(column_name, label)

        # set last item to be the stretchy one
        self.splitter.setStretchFactor(len(self.parent().key_map) - 1, 100000)

        # set size
        self.splitter.setFixedHeight(self.parent().header_height)
        self.setFixedHeight(self.parent().header_height)

    def resetHeaderItems(self):
        self._header_items = OrderedDict()

    def getHeaderItems(self):
        return self._header_items

    def setHeaderItems(self, name, widget):
        self._header_items[name] = widget

    def updateColumnsWidth(self):
        """

        When the splitter is moved, this will update all of the items
        in this column to have the same width as the corresponding
        item in the header
        """
        header_items = self.getHeaderItems()
        for key in list(header_items.keys()):
            widget = header_items[key]
            widget.updateColumnWidth()


class DetailedViewHorizontalHeaderItem(QLabel):
    """
    Individual item in the header
    @widget_list: <list> of <QWidget>
        This is a container for all of the widgets in the column.
    """
    def __init__(self, parent=None, text=None):
        super(DetailedViewHorizontalHeaderItem, self).__init__(parent)
        self.resetWidgetList()
        self.setText(text)
        self.setAlignment(Qt.AlignCenter)

    def getWidgetList(self):
        return self._widget_list

    def appendWidget(self, widget):
        self._widget_list.append(widget)

    def resetWidgetList(self):
        self._widget_list = []

    def updateColumnWidth(self):
        for widget in self.getWidgetList():
            widget.setFixedWidth(self.width())


class DetailedViewItem(QGroupBox):
    """
    A single row in the detailed view
    @json <dict> json data
    """
    def __init__(self, parent=None, jsondata=None):
        super(DetailedViewItem, self).__init__(parent)
        self.json = jsondata
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(self.parent().column_spacing)
        self.setLayout(self.main_layout)
        self.populate()
        self.setMinimumWidth(1)
        self.setStyleSheet("""
            border: None;
            margin: 0px;
        """)

    @property
    def json(self):
        return self._json

    @json.setter
    def json(self, json):
        self._json = json

    def populate(self):
        # set up rest of meta data
        for key in self.parent().key_map:
            try:
                text = self.json[key]
            except KeyError:
                text = 'Not Valid'
            finally:
                widget = QPlainTextEdit()
                widget.setPlainText(text)
                widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.main_layout.addWidget(widget)
                self.parent().hheader.getHeaderItems()[key].appendWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    filedir = '/media/ssd01/library/library/light/texture/card/block'
    model = ImageListModel(filedir=filedir)

    ThumbnailWidget = QListView()
    ThumbnailWidget.setResizeMode(QListView.Adjust)
    ThumbnailWidget.setViewMode(QListView.IconMode)
    ThumbnailWidget.setItemAlignment(Qt.AlignLeft)
    ThumbnailWidget.setIconSize(QSize(50, 50))

    # widget.setProperty('isWrapping', True)
    detailed_view = DetailedViewWidget()
    # initial populate?
    filedir = '/media/ssd01/library/library/light/texture/card/block'
    model = ImageListModel(filedir=filedir)
    detailed_view.setModel(model)
    # detailed_view.header.updateColumnsWidth()

    detailed_view.show()

    thumbnail_widget = ThumbnailViewWidget()
    thumbnail_widget.setModel(model)
    thumbnail_widget.show()

    #ThumbnailWidget.setModel(model)
    #ThumbnailWidget.show()

    sys.exit(app.exec_())



