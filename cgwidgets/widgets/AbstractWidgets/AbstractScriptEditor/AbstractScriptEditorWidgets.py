import math
import json
import os

from qtpy import API_NAME

from qtpy.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QGraphicsView,
    QPushButton,
    QGraphicsItemGroup,
    QGraphicsPolygonItem,
    QOpenGLWidget,
    QGraphicsScene,
    QGraphicsTextItem,
)
from qtpy.QtGui import (
    QCursor,
    QBrush,
    QTransform,
    QColor,
    QPainter,
    QPen,
    QPolygonF,
    QTextBlockFormat,
    QTextCursor
)
from qtpy.QtCore import Qt, QPointF, QPoint, QSize

from .AbstractScriptEditorUtils import Utils as Locals

from cgwidgets.utils import (
    getWidgetAncestorByName,
    getJSONData,
    getCenterOfScreen,
    getWidgetAncestor,
    setAsTransparent,
    setAsTool,
    setAsPopup,
    scaleResolution
)

from cgwidgets.settings import iColor

""" ABSTRACT CLASSES """
class AbstractDesignWidget(object):
    """ Design Widget base class used for all Hotkey/Gesture DesignWidgets

    Attributes:
        button_dict (dict): of all of the buttons
            {"hotkey": QPushButton, "a", QPushButton}
        """
    def __init__(self):
        self.button_dict = {}

    def __name__(self):
        return "__design_widget__"

    def createButton(
        self,
        button_type=None,
        text=None,
        unique_hash=None,
        gesture_points_dict=None,
        index=None
    ):
        if button_type is None:
            return

        elif button_type == "hotkey editor":
            button = HotkeyDesignEditorButton(
                parent=self,
                text=text,
                unique_hash=unique_hash
            )
        elif button_type == "hotkey gui":
            button = HotkeyDesignPopupButton(
                parent=self,
                text=text,
                unique_hash=unique_hash
            )
        elif button_type == "gesture editor":
            button = GestureDesignEditorButton(
                points_list=gesture_points_dict[str(index)]["point_list"],
                text=text,
                center_point=gesture_points_dict[str(index)]["pc"],
                num_points=gesture_points_dict["num_points"],
                hotkey=index,
                type_point=gesture_points_dict[str(index)]["pl"]
            )
            # no idea why it"s not setting with the pos being sent through...
            # so just using the post hack instead =\
            button.setPos(gesture_points_dict["pos"], gesture_points_dict["pos"])
            button.text_item.centerText()
            self.scene().addItem(button)
        elif button_type == "gesture gui":
            button = GestureDesignPopupButton(
                points_list=gesture_points_dict[str(index)]["point_list"],
                text=text,
                center_point=gesture_points_dict[str(index)]["pc"],
                num_points=gesture_points_dict["num_points"],
                hotkey=index,
                type_point=gesture_points_dict[str(index)]["pl"]
            )
            # no idea why it"s not setting with the pos being sent through...
            # so just using the post hack instead =\
            button.setPos(gesture_points_dict["pos"], gesture_points_dict["pos"])
            button.text_item.centerText()
            self.scene().addItem(button)
        return button

    def populate(
        self,
        file_dict,
        item_dict=None,
        button_type=None,
        gesture_points_dict=None,
        r0=None
    ):
        """ Populates the design editor

        This also populates the button dict

        Args:
            file_dict (dict): from the filepath.json for a design item
            item_dict (dict): of {filepath:item} that is stored on the AbstractScriptEditorWidget"""
        # create button layout
        if "hotkey" in button_type:
            self.button_list = [
                ["1", "2", "3", "4", "5"],
                ["q", "w", "e", "r", "t"],
                ["a", "s", "d", "f", "g"],
                ["z", "x", "c", "v", "b"],
            ]
        elif "gesture" in button_type:
            self.button_list = [["0", "1", "2", "3", "4", "5", "6", "7"]]

        for row in self.button_list:
            for item in row:
                unique_hash = None
                # create buttons that are not empty
                if "." in file_dict[item]:
                    if ".py" in file_dict[item]:
                        unique_hash, name = file_dict[item][file_dict[item].rindex("/")+1:].replace(".py", "").split(".")
                    elif ".json" in file_dict[item]:
                        unique_hash, name = file_dict[item][file_dict[item].rindex("/")+1:].replace(".json", "").split(".")
                    if "gesture" in button_type:
                        text = name
                    else:
                        text = "{item}\n{name}".format(item=item, name=name)
                    self.button_dict[item] = self.createButton(
                        button_type=button_type,
                        text=text,
                        unique_hash=unique_hash,
                        gesture_points_dict=gesture_points_dict,
                        index=item
                    )
                    self.button_dict[item].setHotkey(item)

                    # special handling of relative paths
                    item_filepath = file_dict[item]
                    if item_filepath.startswith("../"):
                        item_filepath = item_filepath.replace("..", "/".join(self.filepath().split("/")[:-1]))
                        # print("changing file path from {old_path} to {new_path}".format(old_path=file_dict[item], new_path=item_filepath))

                    self.button_dict[item].setFilepath(item_filepath)
                    #self.button_dict[item].setFilepath(file_dict[item])
                    if item_dict:
                        if file_dict[item] in list(item_dict.keys()):
                            self.button_dict[item].setItem(item_dict[file_dict[item]])
                            self.button_dict[item].setHash(unique_hash)
                    file_type = Locals().checkFileType(item_filepath)

                    self.button_dict[item].setFileType(file_type=file_type)
                    self.button_dict[item].updateButtonColor()

                # Create Empty Buttons
                # Will bypass for the gesture user display
                else:
                    if button_type != "gesture gui":
                        text = item
                        file_type = None
                        self.button_dict[item] = self.createButton(
                            button_type=button_type,
                            text=text,
                            unique_hash=unique_hash,
                            gesture_points_dict=gesture_points_dict,
                            index=item
                        )

                        self.button_dict[item].setHotkey(item)

                        self.button_dict[item].setFileType(file_type=file_type)
                        self.button_dict[item].updateButtonColor()

        self.setButtonSize()

    def updateButtons(self, old_file_path, delete=False):
        """ Updates all of the buttons file paths

        Args:
            old_file_path (str): items previous held filepath
            delete (bool): Determines if this is a delete operation"""

        script_editor_widget = getWidgetAncestorByName(self, "AbstractScriptEditorWidget")
        item_dict = script_editor_widget.scriptWidget().itemDict()
        button_list = self.getButtonDict()
        for key in list(button_list.keys()):
            button = button_list[key]
            if hasattr(button, "file_path"):
                if button.filepath() == old_file_path:
                    # delete button data
                    if delete:
                        button.updateButton(current_item=None)

                    # update button data
                    else:
                        try:
                            item = item_dict[str(button.filepath())]
                            button.updateButton(current_item=item)
                        except KeyError:
                            # item doesn"t exist anymore
                            """ Need to except here, because I"m an idiot, and sometimes I"m updating
                            this multiple times... after its been reset, and I"m to lazy to clean it up"""
                            pass
                    #
                    # # update buttons meta data if name/directory update
                    # if os.path.exists(button.filepath()):
                    #     try:
                    #         item = item_dict[str(button.filepath())]
                    #         button.updateButton(current_item=item)
                    #     except KeyError:
                    #         # item doesn"t exist anymore
                    #         """ Need to except here, because I"m an idiot, and sometimes I"m updating
                    #         this multiple times... after its been reset, and I"m to lazy to clean it up"""
                    #         pass
                    #
                    # # remove buttons meta data if item has been deleted
                    # else:
                    #     button.updateButton(current_item=None)

    """ PROPERTIES """
    def setFilepath(self, file_path):
        self.file_path = file_path

    def filepath(self):
        return self.file_path

    def setHash(self, unique_hash):
        self.hash = unique_hash

    def getHash(self):
        return self.hash

    def setButtonSize(self):
        pass

    def SetButtonDict(self, button_dict):
        self.button_dict = button_dict

    def getButtonDict(self):
        return self.button_dict

    def setItem(self, item):
        self.item = item

    def getItem(self):
        return self.item


class AbstractDesignButtonInterface(object):
    """ Base class used for all Design Buttons (Gesture/Hotkey)

    Attributes:
        border_color (tuple): color of 255 strings to be displayed as the widgets border
            (255, 255, 255)
        border_width (int): width of border of widgets that are active
        item (AbstractBaseItem): Current Script/Gesture/Hotkey design item
        hash (str): unique hash identifier
        hotkey (str): activation hotkey (if valid)

        """

    def __name__(self):
        return "__design_button_widget__"

    """ PROPERTIES """
    def getBorderWidth(self):
        return self._border_width

    def setBorderWidth(self, border_width):
        self._border_width = border_width

    def getBorderColor(self):
        return self._border_color

    def setBorderColor(self, border_color):
        self._border_color = border_color

    def setItem(self, item):
        self.item = item

    def getItem(self):
        return self.item

    def getHash(self):
        return self.hash

    def setHash(self, unique_hash):
        self.hash = unique_hash

    def setHotkey(self, hotkey):
        self.hotkey = hotkey

    def getHotkey(self):
        return self.hotkey

    def setFilepath(self, file_path):
        self.file_path = file_path

    def filepath(self):
        return self.file_path

    def getFileType(self):
        if not hasattr(self, "file_type"):
            return None
        return self.file_type

    def setFileType(self, file_type):
        self.file_type = file_type

    """ METHODS """
    def updateFile(self, file_path=None, delete=False):
        """
        @file_path <str> path to script file
        @design_path <str> path to design file
        """
        item = self.getCurrentItem()
        if not file_path:
            file_path = item.filepath()
        hotkey_dict = self.getHotkeyDict()
        if hotkey_dict:
            if delete is True:
                hotkey_dict[self.getHotkey()] = ""
            else:
                hotkey_dict[self.getHotkey()] = file_path

            # write out json
            design_path = self.getDesignPath()
            if file_path:
                # Writing JSON data
                with open(design_path, "w") as f:
                    json.dump(hotkey_dict, f)

    def updateButton(self, current_item=None):
        if current_item:
            item_type = current_item.getItemType()
            droppable_list = ["script", "gesture", "hotkey"]
            if item_type in droppable_list:
                if isinstance(self, GestureDesignEditorButton):
                    self.setText("%s" % (current_item.text(0)))
                elif isinstance(self, GestureDesignPopupButton):
                    self.setText("%s" % (current_item.text(0)))
                else:
                    self.setText(self.hotkey + "\n%s" % (current_item.text(0)))

                file_path = current_item.filepath()
                self.updateFile(file_path=file_path)
                self.setFilepath(file_path)
                self.setHash(current_item.getHash())
                self.setItem(current_item)
                if os.path.exists(file_path):
                    file_type = Locals().checkFileType(file_path)
                    self.setFileType(file_type)

                else:
                    self.updateButton(current_item=None)
        else:
            self.setText(self.getHotkey())
            delattr(self, "hash")
            delattr(self, "file_path")
            # delattr(self, "item")
            delattr(self, "file_type")

        self.updateButtonColor()


""" HOTKEY WIDGETS """
class AbstractHotkeyDesignWidget(QWidget, AbstractDesignWidget):
    """ AbstractHotkeyDesignWidget base class"""
    def __init__(
        self,
        parent=None,
        item=None,
        file_path="",
        init_pos=None
    ):
        super(AbstractHotkeyDesignWidget, self).__init__(parent)
        if API_NAME == "PySide2":
            AbstractDesignWidget.__init__(self)

    def __name__(self):
        return "__hotkey_editor_widget__"

    def getButtonSize(self):
        width = self.geometry().width() / 5
        height = self.geometry().height() / 4
        return width, height

    """ EVENTS """

    def resizeEvent(self, *args, **kwargs):
        self.setButtonSize()
        return QWidget.resizeEvent(self, *args, **kwargs)


class AbstractHotkeyDesignButtonWidget(QPushButton, AbstractDesignButtonInterface):
    STYLESHEET = """
        color: rgba{TEXT_COLOR};
        border-style: {BORDER_STYLE};
        border-width: {BORDER_WIDTH}px;
        border-radius: {BORDER_RADIUS}px;
        border-color: rgba{BORDER_COLOR};
        background-color: rgba{BACKGROUND_COLOR};
        """

    COLOR_INTENSITY = 100

    FINGERS_LIST = {
        "a": ["1", "q", "a", "z"],
        "s": ["2", "w", "s", "x"],
        "d": ["3", "e", "d", "c"],
        "f": ["4", "r", "f", "v"],
        "g": ["5", "t", "g", "b"]
    }

    def __init__(self, parent=None, text=None, unique_hash=None):
        super(AbstractHotkeyDesignButtonWidget, self).__init__(parent)
        if API_NAME == "PySide2":
            AbstractDesignButtonInterface.__init__(self)
        self.setText(text)
        self.setHotkey(text)
        self.setAcceptDrops(True)
        self.clicked.connect(self.execute)
        self.setHash(unique_hash)
        self._border_width = 6
        self.__setupBorderColor()

    def __setupBorderColor(self):
        """ Sets the current borderColor for this button
        """
        # setup border color
        color_intensity = AbstractHotkeyDesignButtonWidget.COLOR_INTENSITY

        hotkey = self.getHotkey().split("\n")[0]
        if hotkey in ["a", "s", "d", "f", "g"]:
            color_intensity = color_intensity + (color_intensity * 2)
            if color_intensity > 255:
                color_intensity = 255

        if hotkey in AbstractHotkeyDesignButtonWidget.FINGERS_LIST["a"]:
            border_color = "(%s,0,0,255)" % str(float(color_intensity) * .75)
        elif hotkey in AbstractHotkeyDesignButtonWidget.FINGERS_LIST["s"]:
            border_color = "(0,%s,0,255)" % str(float(color_intensity) * .75)
        elif hotkey in AbstractHotkeyDesignButtonWidget.FINGERS_LIST["d"]:
            border_color = "(0,0,%s,255)" % str(float(color_intensity) * .75)
        elif hotkey in AbstractHotkeyDesignButtonWidget.FINGERS_LIST["f"]:
            border_color = "(%s,%s,0,255)" % (str(float(color_intensity) * .75), str(float(color_intensity) * .75))
        elif hotkey in AbstractHotkeyDesignButtonWidget.FINGERS_LIST["g"]:
            border_color = "(%s,0,%s,255)" % (str(float(color_intensity) * .75), str(float(color_intensity) * .75))

        self.setBorderColor(border_color)

    def updateButtonColor(self, hover=False, drag_active=False):
        """ Updates the buttons colors.

        Args:
            hover (bool): determines if the user is currently hovering over the widget or not
        """
        # get border color
        background_color = iColor["rgba_background_01"]
        if hover:
            border_color = iColor["rgba_selected_hover_2"]
            text_color = iColor["rgba_text_hover"]
        else:
            border_color = self.getBorderColor()
            text_color = iColor["rgba_text"]

        if hasattr(self, "file_type"):
            # hotkey
            if self.getFileType() == "hotkey":
                style_sheet = AbstractHotkeyDesignButtonWidget.STYLESHEET.format(
                    BORDER_COLOR=border_color,
                    BORDER_WIDTH=self.getBorderWidth(),
                    BORDER_RADIUS=self.getBorderWidth() * 3,
                    BORDER_STYLE="double",
                    BACKGROUND_COLOR=background_color,
                    TEXT_COLOR=text_color)

            # script
            elif self.getFileType() == "script":
                style_sheet = AbstractHotkeyDesignButtonWidget.STYLESHEET.format(
                    BORDER_COLOR=border_color,
                    BORDER_WIDTH=self.getBorderWidth(),
                    BORDER_RADIUS=self.getBorderWidth() * 3,
                    BORDER_STYLE="solid",
                    BACKGROUND_COLOR=background_color,
                    TEXT_COLOR=text_color)

            # inactive
            else:
                # DRAG ENTER COLOR
                if drag_active:
                    style_sheet = AbstractHotkeyDesignButtonWidget.STYLESHEET.format(
                        BORDER_COLOR=border_color,
                        BORDER_WIDTH=self.getBorderWidth(),
                        BORDER_RADIUS=self.getBorderWidth() * 3,
                        BORDER_STYLE="dotted",
                        BACKGROUND_COLOR=iColor["rgba_background_01"],
                        TEXT_COLOR=text_color)

                # INACTIVE COLOR
                else:
                    style_sheet = AbstractHotkeyDesignButtonWidget.STYLESHEET.format(
                        BORDER_COLOR=iColor["rgba_background_00"],
                        BORDER_WIDTH=self.getBorderWidth(),
                        BORDER_RADIUS=self.getBorderWidth() * 3,
                        BORDER_STYLE="solid",
                        BACKGROUND_COLOR=iColor["rgba_background_00"],
                        TEXT_COLOR=iColor["rgba_text_disabled"])

        else:
            style_sheet = AbstractHotkeyDesignButtonWidget.STYLESHEET.format(
                BORDER_COLOR=iColor["rgba_background_00"],
                BORDER_WIDTH=self.getBorderWidth(),
                BORDER_RADIUS=self.getBorderWidth() * 3,
                BORDER_STYLE="solid",
                BACKGROUND_COLOR=iColor["rgba_background_00"],
                TEXT_COLOR=iColor["rgba_text_disabled"])

        self.setStyleSheet(style_sheet)

    def enterEvent(self, event):
        self.updateButtonColor(hover=True)
        return QPushButton.enterEvent(self, event)

    def leaveEvent(self, event):
        self.updateButtonColor()
        return QPushButton.leaveEvent(self, event)


class HotkeyDesignEditorWidget(AbstractHotkeyDesignWidget):
    """ Hotkey designer displayed as a widget in the DesignTab

    Displayed on right side when user clicks on a "HotkeyDesign" item
    The individual buttons inside of this are the HotkeyDesignEditorButtons
    """
    def __init__(self, parent=None, item=None, file_path=""):
        super(HotkeyDesignEditorWidget, self).__init__(parent)
        # set up default attributes
        self.setFilepath(file_path)
        # self.button_dict = {}
        file_dict = getJSONData(self.filepath())

        script_editor_widget = getWidgetAncestorByName(self.parentWidget(), "AbstractScriptEditorWidget")
        item_dict = script_editor_widget.scriptWidget().itemDict()
        self.item = item
        self.populate(file_dict, item_dict=item_dict, button_type="hotkey editor")
        # self.setStyleSheet("background-color:rgba(255,0,0,255);")

    def setButtonSize(self):
        button_width, button_height = self.getButtonSize()
        for row_index, row in enumerate(self.button_list):
            for column_index, item in enumerate(row):
                x_pos = column_index * button_width
                y_pos = row_index * button_height
                self.button_dict[item].setGeometry(
                    x_pos,
                    y_pos,
                    button_width,
                    button_height
                )

    def setItem(self, item):
        self.item = item

    def getItem(self):
        return self.item

    def resizeEvent(self, *args, **kwargs):
        self.setButtonSize()
        return QWidget.resizeEvent(self, *args, **kwargs)


class HotkeyDesignEditorButton(AbstractHotkeyDesignButtonWidget):
    """Individiual Buttons displayed in the HotkeyDesign Widget"""
    def __init__(
        self,
        parent=None,
        text=None,
        unique_hash=None
    ):
        super(HotkeyDesignEditorButton, self).__init__(parent, text=text, unique_hash=unique_hash)
        self.setAcceptDrops(True)

    def __name__(self):
        return "__design_button__"

    def execute(self):
        if hasattr(self, "item"):
            tw = self.item.treeWidget()
            item = self.getItem()
            tw.setCurrentItem(item)
            tw.showTab(item)

    def getCurrentItem(self):
        script_editor_widget = getWidgetAncestorByName(self, "AbstractScriptEditorWidget")
        current_item = script_editor_widget.scriptWidget().currentItem()
        return current_item

    def getHotkeyDict(self):
        """Returns the hotkey dictionary or None"""
        if os.path.exists(self.parent().filepath()):
            return getJSONData(self.parent().filepath())
        else:
            return None

    def getDesignPath(self):
        return self.parent().filepath()

    """ EVENTS """
    def dragEnterEvent(self, event, *args, **kwargs):
        # update background color
        current_item = self.getCurrentItem()
        item_type = current_item.getItemType()
        droppable_list = ["script", "hotkey"]
        if item_type in droppable_list:
            self.updateButtonColor(hover=True, drag_active=True)
            event.accept()

        return QPushButton.dragEnterEvent(self, event, *args, **kwargs)

    def dragLeaveEvent(self, event):
        self.updateButtonColor()
        return QPushButton.dragLeaveEvent(self, event)

    def dropEvent(self, event, *args, **kwargs):
        self.updateButton(current_item=self.getCurrentItem())

        return QPushButton.dropEvent(self, event, *args, **kwargs)

    def mouseReleaseEvent(self, event, *args, **kwargs):
        if event.button() == Qt.MiddleButton:
            if hasattr(self, "file_path"):
                self.updateFile(delete=True)
                self.updateButton()
        return QPushButton.mouseReleaseEvent(self, event, *args, **kwargs)


""" GESTURE """
class GestureDesignWidget(QGraphicsView, AbstractDesignWidget):
    def __init__(
        self,
        parent=None,
        item=None,
        file_path="",
        init_pos=None,
        display_type=None,
        script_list=None,
        size=50
    ):
        super(GestureDesignWidget, self).__init__(parent)
        if API_NAME == "PySide2":
            AbstractDesignWidget.__init__(self)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalScrollBar().setStyleSheet("height:0px")
        self.verticalScrollBar().setStyleSheet("width:0px")
        #self.setStyleSheet("background-color: rgba(0,255,255,255);")

        #color = QColor(1,1,1,255)
        #self.setBackgroundBrush(QBrush(color, Qt.SolidPattern))

    def __name__(self):
        return "__gesture_editor_widget__"

    """ EVENTS"""

    def updatePolygons(
        self,
        num_points=8,
        display_type="gesture editor",
        size=None
    ):
        script_editor_widget = getWidgetAncestorByName(self, "AbstractScriptEditorWidget")

        for item in self.scene().items():
            self.scene().removeItem(item)

        self.setMaximumSize(size, size)
        outer_radius = size * .25
        inner_radius = outer_radius * self.poly_width

        file_dict = getJSONData(self.filepath())

        item_dict = script_editor_widget.scriptWidget().itemDict()
        self.drawPolygons(
            num_points=num_points,
            display_type=display_type,
            r0=outer_radius,
            r1=inner_radius,
            size=size,
            file_dict=file_dict,
            item_dict=item_dict
        )

    def drawPolygons(
        self,
        num_points=None,
        display_type=None,
        r0=100,
        r1=40,
        size=None,
        item_dict=None,
        file_dict=None
    ):
        """
        @num_points <int> total number of segments to draw
        @returns <list> of <Polygon>
        """
        def getPoints(index, num_points, offset, r0, r1):
            """
            returns the points to draw the polygon button and the center coordinate
            @return: 5 * <QPointF> , p0, p1, p2, p3, pc
            @index: <int> index number
            @num_points <int> total number of points in the primitive
            @offset <float> the gap between each primitive
            """
            # ===================================================================
            # outer left
            # ===================================================================
            # x
            rl = float(r0 + 10)
            r0 -= 20
            x0 = (
                r0 * math.cos(
                    2 * math.pi * ((index + .5) / num_points) + offset
                )
            )
            # y
            y0 = (
                r0 * math.sin(
                    2 * math.pi * ((index + .5) / num_points) + offset
                )
            )
            p0 = QPointF(x0, y0)

            # ===================================================================
            # inner left
            # ===================================================================
            # x
            x1 = (
                r1 * math.cos(
                    2 * math.pi * ((index + .5) / num_points) + offset
                )
            )
            # y
            y1 = (
                r1 * math.sin(
                    2 * math.pi * ((index + .5) / num_points) + offset
                )
            )
            p1 = QPointF(x1, y1)
            # ===================================================================
            # outer right
            # ===================================================================
            # x
            x2 = (
                r0 * math.cos(
                    2 * math.pi * ((index - .5) / num_points) - offset
                )
            )
            # y
            y2 = (
                r0 * math.sin(
                    2 * math.pi * ((index - .5) / num_points) - offset
                )
            )
            p2 = QPointF(x2, y2)

            # inner right
            # x
            x3 = (
                r1 * math.cos(
                    2 * math.pi * ((index - .5) / num_points) - offset
                )
            )
            # y
            y3 = (
                r1 * math.sin(
                    2 * math.pi * ((index - .5) / num_points) - offset
                )
            )
            p3 = QPointF(x3, y3)

            # Center Point of polygon
            x4 = (
                rc * math.cos(
                    2 * math.pi * ((index) / num_points)
                )
            )
            # y
            y4 = (
                rc * math.sin(
                    2 * math.pi * ((index) / num_points)
                )
            )
            p4 = QPointF(x4, y4 - 20)

            # Add inner points to list for central button
            r2 = r1 * .85
            x5 = (
                r2 * math.cos(
                    2 * math.pi * ((index + .5) / num_points)
                )
            )
            # y
            y5 = (
                r2 * math.sin(
                    2 * math.pi * ((index + .5) / num_points)
                )
            )
            p5 = QPointF(x5, y5)
            inner_polygon_points.append(p5)

            # Type Label
            # x
            x6 = (
                rl * math.cos(
                    2 * math.pi * ((index) / num_points) + offset
                )
            )
            # y
            y6 = (
                rl * math.sin(
                    2 * math.pi * ((index) / num_points) + offset
                )
            )
            p6 = QPointF(x6, y6)

            # p0-3 polygon
            # p4 = point center of polygon (for text)
            # p5 = center button...
            # p6 = point label
            return p0, p1, p2, p3, p4, p5, p6
        # set up geometry

        self.scene().setSceneRect(0, 0, size, size)
        # initial attributes
        inner_polygon_points = []
        offset = -.05
        item_list = []
        polygon_points_dict = {}
        polygon_points_dict["num_points"] = num_points
        polygon_points_dict["pos"] = size * .5
        rc = (((r0 - r1) * .5) + r1)

        # create polygon segments
        for index in range(num_points):
            p0, p1, p2, p3, pc, p4, pl = getPoints(index, num_points, offset, r0, r1)
            points_list = [p0, p1, p3, p2, p0]
            polygon_points_dict[str(index)] = {}
            polygon_points_dict[str(index)]["point_list"] = points_list
            polygon_points_dict[str(index)]["pc"] = pc
            polygon_points_dict[str(index)]["pl"] = pl

        # populate
        self.populate(
            file_dict=file_dict,
            item_dict=item_dict,
            button_type=display_type,
            gesture_points_dict=polygon_points_dict,
            r0=r0
        )

        # rotate outside labels?
        """
        for index, key in enumerate(sorted(list(self.getButtonDict().keys()))):
            button = self.getButtonDict()[key]
            label = button.label_item
            self.rotate(label, ((360/num_points) * index) + 90)
        """

        return item_list

    def rotate(self, item, angle):
        sina = math.sin(math.radians(angle))
        cosa = math.cos(math.radians(angle))
        translationTransform = QTransform(
            1, 0, 0,
            0, 1, 0,
            0, 0, 1
        )

        rotationTransform = QTransform(
            cosa, sina, -sina, cosa, 0, 0
        )

        scalingTransform = QTransform(
            1, 0, 0,
            0, 1, 0,
            0, 0, 1
        )
        transform = scalingTransform * rotationTransform * translationTransform;
        item.setTransform(rotationTransform)

    def wheelEvent(self, *args, **kwargs):
        """
        disables scrolling events
        """
        pass

    def dropEvent(self, event, *args, **kwargs):
        event.setDropAction(Qt.CopyAction)
        return QGraphicsView.dropEvent(self, event, *args, **kwargs)


class GestureDesignButtonWidget(QGraphicsItemGroup, AbstractDesignButtonInterface):
    """
    @points_list: <list> of <QPointF> for building the polygon
    @text: <str> display text
    @center_point: <QPointF> center point of each polygon
    @num_points: <int> total number of buttons
    """
    def __init__(
            self,
            parent=None,
            points_list=None,
            text=None,
            center_point=None,
            num_points=None
        ):
        super(GestureDesignButtonWidget, self).__init__(parent)
        if API_NAME == "PySide2":
            AbstractDesignButtonInterface.__init__(self)

    def setText(self, text):
        self.text_item.setPlainText(text)
        self.text_item.centerText()

    def rotate(self, item, angle):
        sina = math.sin(math.radians(angle))
        cosa = math.cos(math.radians(angle))
        translationTransform = QTransform(
            1, 0, 0,
            0, 1, 0,
            0, 0, 1
        )

        rotationTransform = QTransform(
            cosa, sina, -sina, cosa, 0, 0
        )

        scalingTransform = QTransform(
            1, 0, 0,
            0, 1, 0,
            0, 0, 1
        )
        transform = scalingTransform * rotationTransform * translationTransform;
        item.setTransform(transform)

    def updateButtonColor(self):
        #self.label_item.setPlainText("None")

        pen = self.poly_item.pen()
        width = 2
        pen.setWidth(width)
        pen_style = Qt.CustomDashLine
        file_type = self.getFileType()
        # set up morse code dots...
        if file_type is None:
            text = "None"
            color = QColor(*iColor["rgba_text"])

            morse_code = [
                3, 1, 1, 3,
                3, 1, 3, 1, 3, 3,
                3, 1, 1, 3,
                1, 7
            ]
        else:
            if file_type == "hotkey":
                text = "hotkey"
                color = QColor(128, 0, 0)
                morse_code = [
                    1, 1, 1, 1, 1, 1, 1, 3,
                    3, 1, 3, 1, 3, 3,
                    3, 3,
                    3, 1, 1, 1, 3, 3,
                    1, 3,
                    3, 1, 1, 1, 3, 3, 3, 3
                ]
                """
                notatroll = [
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 3,
                    1, 3,
                    3, 1, 1, 3,
                    1, 1, 1, 3,
                    1, 1, 1, 1, 1, 7
                ]
                notatroll = [x * width for x in notatroll]
                """
            elif file_type == "gesture":
                text = "gesture"
                color = QColor(0, 0, 128)
                morse_code = [
                    3, 1, 3, 1, 1, 3,
                    1, 3,
                    1, 1, 1, 1, 1, 3,
                    3, 3,
                    1, 1, 1, 1, 3, 3,
                    1, 1, 3, 1, 1, 3,
                    1, 3,
                ]
            elif file_type == "script":
                text = "script"
                color = QColor(0, 128, 0)
                morse_code = [
                    1, 1, 1, 1, 1, 3,
                    3, 1, 1, 1, 3, 1, 1, 3,
                    1, 1, 3, 1, 1, 3,
                    1, 1, 1, 3,
                    1, 1, 3, 1, 3, 1, 1, 3,
                    3, 7
                ]

        morse_code = [x * width for x in morse_code]
        pen.setDashPattern(morse_code)
        pen.setStyle(pen_style)

        # set text
        # self.label_item.setPlainText(text)
        self.text_item.centerText()
        pen.setColor(color)
        self.poly_item.setPen(pen)
        self.text_item.setDefaultTextColor(QColor(*iColor["rgba_text"]))


class GestureDesignPolyWidget(QGraphicsPolygonItem, AbstractDesignButtonInterface):
    def __init__(self, parent=None, points_list=None):
        super(GestureDesignPolyWidget, self).__init__(parent)
        if API_NAME == "PySide2":
            AbstractDesignButtonInterface.__init__(self)
        self.drawPolygon(points_list)
        """
        # setup color
        brush = QBrush()
        brush_color = QColor()
        brush_color.setRgbF(1.0, 1.0, 0.0)
        brush.setColor(brush_color)
        brush.setStyle(Qt.SolidPattern)
        self.setBrush(brush)
        """

        # hide border
        pen = self.pen()
        pen_color = QColor()
        pen_color.setRgb(255, 255, 255, 255)
        pen.setColor(pen_color)
        self.setPen(pen)
        pen.setStyle(Qt.DotLine)

    def drawPolygon(self, points_list):
        polygon = QPolygonF()
        for point in points_list:
            polygon.append(point)
        self.setPolygon(polygon)


class GestureDesignEditorWidget(GestureDesignWidget):
    def __init__(
        self,
        parent=None,
        item=None,
        file_path="",
        init_pos=None,
        display_type=None,
        script_list=None,
        size=50
    ):
        super(GestureDesignEditorWidget, self).__init__(parent)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        script_editor_widget = getWidgetAncestorByName(self, "AbstractScriptEditorWidget")
        self.script_list = script_list
        self.setItem(item)
        self.setFilepath(file_path)
        self.poly_width = .5
        # init settings
        outer_radius = size * .25
        inner_radius = outer_radius * self.poly_width

        # set up graphics scene
        self.gl_widget = QOpenGLWidget()
        self.setViewport(self.gl_widget)
        scene = QGraphicsScene()
        self.setScene(scene)

        # set up buttons
        file_dict = getJSONData(self.filepath())
        script_editor_widget = getWidgetAncestorByName(self, "AbstractScriptEditorWidget")
        item_dict = script_editor_widget.scriptWidget().itemDict()
        self.drawPolygons(
            num_points=8,
            display_type="gesture editor",
            r0=outer_radius,
            r1=inner_radius,
            size=size,
            item_dict=item_dict,
            file_dict=file_dict
        )
        # set scene display
        self.setMaximumSize(size, size)
        color = QColor(*iColor["rgba_background_01"])
        self.setBackgroundBrush(QBrush(color, Qt.SolidPattern))
        self.setStyleSheet("border:None")


class GestureDesignEditorButton(GestureDesignButtonWidget):
    def __init__(
        self,
        parent=None,
        text=None,
        unique_hash=None,
        points_list=None,
        center_point=None,
        num_points=None,
        pos=None,
        hotkey=None,
        type_point=None
    ):
        super(GestureDesignEditorButton, self).__init__(parent)
        # set up items
        self.poly_item = GestureDesignPolyWidget(points_list=points_list)

        self.text_item = GestureDesignPopupTextItem(
            text=text, hotkey=hotkey, pos=type_point
        )
        self.text_item.setPos(center_point)

        # parent items
        self.addToGroup(self.poly_item)
        self.text_item.setParentItem(self.poly_item)

        # set up attributes
        self.setHotkey(hotkey)
        self.setAcceptDrops(True)
        self.text_item.setAcceptDrops(False)
        self.poly_item.setAcceptDrops(False)
        self.setHash(unique_hash)

        # setup default style
        # brush = QBrush(QColor(255, 255, 255, 255))
        # self.poly_item.setPen(brush)
        # self.text_item.setPen(brush)

    def execute(self):
        if hasattr(self, "item"):
            tw = self.item.treeWidget()
            item = self.getItem()
            tw.setCurrentItem(item)
            tw.showTab(item)

    """ NECESSARY """

    def getDesignPath(self):
        """
        @returns: path on disk to the design file
        """
        return self.getView().filepath()

    def getHotkeyDict(self):
        """
        @returns: dictionary of design hotkeys
        """
        if os.path.exists(self.getView().filepath()):
            return getJSONData(self.getView().filepath())

    def getView(self):
        return self.scene().views()[0]

    def getScriptList(self):
        return self.getView().script_list

    def getCurrentItem(self):
        current_item = self.getScriptList().currentItem()
        return current_item

    """ EVENTS """

    def dragEnterEvent(self, event, *args, **kwargs):
        current_item = self.getCurrentItem()
        item_type = current_item.getItemType()
        droppable_list = ["script", "gesture", "hotkey"]
        if item_type in droppable_list:
            event.accept()

        return QGraphicsItemGroup.dragEnterEvent(self, event, *args, **kwargs)

    def dropEvent(self, event, *args, **kwargs):
        self.updateButton(current_item=self.getCurrentItem())
        return QGraphicsItemGroup.dropEvent(self, event, *args, **kwargs)

    def mousePressEvent(self, event, *args, **kwargs):
        if event.button() == Qt.MiddleButton:
            if hasattr(self, "file_path"):
                self.updateFile(delete=True)
                self.updateButton()
        elif event.button() == Qt.LeftButton:
            self.execute()
        return QGraphicsItemGroup.mousePressEvent(self, event, *args, **kwargs)


class GestureDesignEditorTextItem(QGraphicsTextItem):
    def __init__(
            self,
            parent=None,
            text=None,
            hotkey=None,
            pos=None
        ):

        super(GestureDesignEditorTextItem, self).__init__(parent)
        self.setPlainText(text)
        self.hotkey = hotkey
        self.orig_point = pos
        self.centerText()

    def centerText(self):
        """
        Centers the text, and moves the text back to the
        center of the button
        @update_pos <bool> determines if the text should have its
        position offset to compensate for centering...
        """
        
        pos = self.orig_point
        width = self.boundingRect().width()
        # center text
        self.setTextWidth(width)
        text_format = QTextBlockFormat()

        xpos = pos.x() - (width * .5)
        text_format.setAlignment(Qt.AlignCenter)

        cursor = self.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(text_format)
        cursor.clearSelection()
        self.setTextCursor(cursor)

        ypos = pos.y()

        
        if self.hotkey in "123":
            ypos -= 20
        elif self.hotkey in "567":
            ypos += 20
        elif self.hotkey == "0":
            xpos -= 15
        elif self.hotkey == "4":
            xpos += 15
        
        # specific handlers to center based on awkward shapes...
        new_pos = QPointF(xpos, ypos)
        self.setPos(new_pos)


class GestureDesignPopupWidget(GestureDesignWidget):
    def __init__(
        self,
        parent=None,
        file_path="",
        init_pos=QCursor.pos(),
        size=500
    ):
        super(GestureDesignPopupWidget, self).__init__(parent)
        self.setFilepath(file_path)
        self.poly_width = .85

        # init settings
        outer_radius = size * .5
        inner_radius = outer_radius * self.poly_width

        # set up graphics scene
        self.gl_widget = QOpenGLWidget()
        self.setViewport(self.gl_widget)
        scene = QGraphicsScene()
        self.setScene(scene)

        # set up buttons
        file_dict = getJSONData(self.filepath())

        self.drawPolygons(
            num_points=8,
            display_type="gesture gui",
            r0=outer_radius,
            r1=inner_radius,
            size=size,
            file_dict=file_dict
        )

        # set scene display
        self.setMaximumSize(size*5, size*5)


class GestureDesignPopupButton(GestureDesignButtonWidget):
    def __init__(
        self,
        parent=None,
        text=None,
        unique_hash=None,
        points_list=None,
        center_point=None,
        num_points=None,
        pos=None,
        hotkey=None,
        type_point=None
    ):
        super(GestureDesignPopupButton, self).__init__(parent)
        # set up items
        self.poly_item = GestureDesignPolyWidget(points_list=points_list)

        self.text_item = GestureDesignPopupTextItem(
            text=text, hotkey=hotkey, pos=type_point
        )
        self.text_item.setPos(type_point)

        # parent items
        self.addToGroup(self.poly_item)
        self.text_item.setParentItem(self.poly_item)

        # set up attributes
        self.setHotkey(hotkey)
        self.setAcceptHoverEvents(True)
        self.text_item.setAcceptHoverEvents(False)
        self.poly_item.setAcceptHoverEvents(False)
        #self.label_item.setAcceptHoverEvents(False)
        self.setHash(unique_hash)

    def execute(self):
        self.scene().views()[0].parent().close()

        if self.getFileType() == "script":
            if os.path.exists(self.filepath()):
                environment = dict(locals(), **globals())
                #environment.update(self.importModules())
                with open(self.filepath()) as script_descriptor:
                    exec(script_descriptor.read(), environment, environment)
        elif self.getFileType() == "hotkey":
            # katana_main = UI4.App.MainWindow.GetMainWindow()
            pos = QCursor.pos()
            popup_menu_widget = PopupHotkeyMenu(file_path=self.filepath(), pos=pos)
            popup_menu_widget.show()
        elif self.getFileType() == "gesture":
            # katana_main = UI4.App.MainWindow.GetMainWindow()
            popup_gesture_widget = PopupGestureMenu(file_path=self.filepath())
            popup_gesture_widget.show()

    def hoverEnterEvent(self, *args, **kwargs):
        if hasattr(self, "file_path"):
            self.execute()
        return GestureDesignButtonWidget.hoverEnterEvent(self, *args, **kwargs)


class GestureDesignPopupTextItem(QGraphicsTextItem):
    def __init__(
        self,
        parent=None,
        text=None,
        hotkey=None,
        pos=None
    ):

        super(GestureDesignPopupTextItem, self).__init__(parent)
        self.setPlainText(text)
        self.hotkey = hotkey
        self.orig_point = pos
        self.centerText()

    def centerText(self):
        """
        Centers the text, and moves the text back to the
        center of the button
        @update_pos <bool> determines if the text should have its
        position offset to compensate for centering...
        """
        
        pos = self.orig_point
        width = self.boundingRect().width()
        # center text
        self.setTextWidth(width)
        text_format = QTextBlockFormat()

        # center
        if self.hotkey in "26":
            xpos = pos.x() - (width * .5)
            text_format.setAlignment(Qt.AlignCenter)
        # right
        elif self.hotkey in "107":
            xpos = pos.x()
            text_format.setAlignment(Qt.AlignRight)
            pass #align right
        # left
        elif self.hotkey in "345":
            xpos = pos.x() - (width)
            text_format.setAlignment(Qt.AlignLeft)
        cursor = self.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(text_format)
        cursor.clearSelection()
        self.setTextCursor(cursor)

        ypos = pos.y() - 15

        """
        if self.hotkey in "123":
            ypos -= 20
        elif self.hotkey in "567":
            ypos += 20
        elif self.hotkey == "0":
            xpos -= 15
        elif self.hotkey == "4":
            xpos += 15
        """
        # specific handlers to center based on awkward shapes...
        new_pos = QPointF(xpos, ypos)
        self.setPos(new_pos)


""" POPUP MENUS """
"""

Hierarchy:
    PopupHotkeyMenu --> (QWidget)
        |- QVBoxLayout
            |- """

class HotkeyDesignPopupWidget(AbstractHotkeyDesignWidget):
    def __init__(self, parent=None, item=None, file_path="", init_pos=None):
        super(HotkeyDesignPopupWidget, self).__init__(parent)
        # set up default attributes
        self.setFilepath(file_path)
        self.button_dict = {}
        file_dict = getJSONData(self.filepath())

        self.init_pos = init_pos
        self.populate(file_dict, button_type="hotkey gui")

    def setButtonSize(self):
        """Sets the button size and position, will be offset to simulate a keyboard layout"""
        button_spacing = .9
        button_width, button_height = self.getButtonSize()
        offset_amount = button_width * .2
        modified_button_width = (
            (float(button_width) - offset_amount)
            + (offset_amount * .25)
        )
        for row_index, row in enumerate(self.button_list):
            offset = (row_index*offset_amount)
            for column_index, item in enumerate(row):
                x_pos = (column_index * modified_button_width) + offset
                y_pos = row_index * button_height
                self.button_dict[item].setGeometry(
                    int(x_pos),
                    int(y_pos),
                    int(modified_button_width * button_spacing),
                    int(button_height * button_spacing)
                )

    def keyPressEvent(self, event, *args, **kwargs):
        key = event.text()
        button_dict = self.getButtonDict()
        if key in button_dict.keys():
            button_dict[key].execute()
        elif Qt.Key_Escape:
            self.parent().close()
        return QWidget.keyPressEvent(self, event,  *args, **kwargs)


class HotkeyDesignPopupButton(AbstractHotkeyDesignButtonWidget):
    def __init__(self, parent=None, text=None, unique_hash=None):
        super(HotkeyDesignPopupButton, self).__init__(parent, text=text, unique_hash=unique_hash)
        self.setAcceptDrops(True)
        self.clicked.connect(self.execute)

    def execute(self):
        getWidgetAncestor(self, PopupHotkeyMenu).close()
        if self.getFileType() == "script":
            # execute file
            if os.path.exists(self.filepath()):
                environment = dict(locals(), **globals())
                with open(self.filepath()) as script_descriptor:
                    exec(script_descriptor.read(), environment, environment)
        elif self.getFileType() == "hotkey":
            self.showHotkeyDesign(self.filepath())
        elif self.getFileType() == "gesture":
            gesture_menu = PopupGestureMenu(self, file_path=self.filepath())
            gesture_menu.show()

    def showHotkeyDesign(self, file_path):
        pos = self.parentWidget().init_pos
        popup_hotkey_menu = PopupHotkeyMenu(self, file_path=file_path, pos=pos)
        popup_hotkey_menu.show()


class PopupHotkeyMenu(QWidget):
    """ Popup Hotkey Menu

    Attributes:
        popup_stack (list): of strings of the current paths that the user
            has clicked to get to the current menu"""
    def __init__(self, parent=None, file_path=None, pos=None, size=scaleResolution(QSize(1800, 600))):
        super(PopupHotkeyMenu, self).__init__(parent)

        # create attrs
        self._size = size
        if not pos:
            pos = getCenterOfScreen()
        self._popup_stack = []

        # setup style
        self.move(pos)
        self.setSize(size)
        setAsTransparent(self)
        setAsPopup(self)

        # create layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(200, 100, 200, 100)
        self._previous_item = QPushButton("Previous Item")
        self._next_item = QPushButton("Next Item")
        self._design_widget = HotkeyDesignPopupWidget(self, file_path=file_path, init_pos=pos)
        self._design_widget.setFocus()
        main_layout.addWidget(self._design_widget)

    def paintEvent(self, event=None):
        """ Set transparency """
        painter = QPainter(self)
        painter.setOpacity(0.75)
        bg_color = QColor(32, 32, 32, 255)
        painter.setBrush(bg_color)
        painter.setPen(QPen(bg_color))

        # ellipse
        ellipse_size = scaleResolution(QSize(900, 700))
        painter.drawEllipse(QPoint(self.width() * 0.5, self.height() * 0.5), ellipse_size.width(), ellipse_size.height())

        # chamfered corners
        # corner_radius = 75
        # poly_points = [
        #     QPoint(corner_radius, 0),
        #     QPoint(self.width() - (corner_radius), 0),
        #     QPoint(self.width(), corner_radius),
        #     QPoint(self.width(), self.height() - (corner_radius)),
        #     QPoint(self.width() - (corner_radius), self.height()),
        #     QPoint(corner_radius, self.height()),
        #     QPoint(0, self.height() - (corner_radius)),
        #     QPoint(0, corner_radius)
        # ]
        # polygon = QPolygonF()
        # for point in poly_points:
        #     polygon.append(point)
        # painter.drawPolygon(polygon)
        #painter.drawRect(self.window().rect())

    def setSize(self, size):
        self._size = size
        self.setGeometry(
            int(self.pos().x() - (size.width() * 0.5)),
            int(self.pos().y() - (size.height() * 0.5)),
            size.width(),
            size.height())


class PopupGestureMenu(QWidget):
    def __init__(self, parent=None, file_path=None, pos=None, size=300, arbitrary_scaler=5):
        super(PopupGestureMenu, self).__init__(parent)

        # setup attrs
        if not pos:
            pos = QCursor.pos()

        # setup style
        setAsTransparent(self)
        setAsPopup(self)

        self.setGeometry(
            int(pos.x() - size * arbitrary_scaler * .5),
            int(pos.y() - size * arbitrary_scaler * .5),
            int(size * arbitrary_scaler),
            int(size * arbitrary_scaler)
        )

        # create main layout
        QVBoxLayout(self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        design_widget = GestureDesignPopupWidget(self, file_path=file_path, init_pos=pos, size=size)
        self.layout().addWidget(design_widget)

        # set focus
        design_widget.setFocusPolicy(Qt.StrongFocus)
        design_widget.setFocus()


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)

    hotkey_file_path = "/home/brian/.cgwidgets/.scripts/1540676548115043584.HotkeyDesign.json"
    # hotkey_file_path = "/home/brian/.cgwidgets/.scripts/991172910425919104.hotkey2.json"
    popup_widget = PopupHotkeyMenu(file_path=hotkey_file_path)

    popup_widget.show()
    # gesture_file_path = "/media/ssd01/dev/katana/KatanaResources_old/Scripts/designs/7297414313744113664.GestureDesign.json"
    # gesture_widget = PopupGestureMenu(file_path=gesture_file_path)
    # gesture_widget.show()

    sys.exit(app.exec_())
