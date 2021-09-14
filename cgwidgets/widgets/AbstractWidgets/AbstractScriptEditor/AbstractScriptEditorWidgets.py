
import math
import json
import os

from qtpy.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QGraphicsView,
    QGraphicsItem,
    QPushButton,
    QGraphicsItemGroup,
    QGraphicsPolygonItem,
    QOpenGLWidget,
    QGraphicsScene,
    QGraphicsTextItem,
)
from qtpy.QtGui import (
    QCursor,
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
    setAsPopup
)

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
        return '__design_widget__'

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

        elif button_type == 'hotkey editor':
            button = HotkeyDesignEditorButton(
                parent=self,
                text=text,
                unique_hash=unique_hash
            )
        elif button_type == 'hotkey gui':
            button = HotkeyDesignPopupButton(
                parent=self,
                text=text,
                unique_hash=unique_hash
            )
        elif button_type == 'gesture editor':
            button = GestureDesignEditorButton(
                points_list=gesture_points_dict[str(index)]['point_list'],
                text=text,
                center_point=gesture_points_dict[str(index)]['pc'],
                num_points=gesture_points_dict['num_points'],
                hotkey=index,
                type_point=gesture_points_dict[str(index)]['pl']
            )
            # no idea why it's not setting with the pos being sent through...
            # so just using the post hack instead =\
            button.setPos(gesture_points_dict['pos'], gesture_points_dict['pos'])
            button.text_item.centerText()
            self.scene().addItem(button)
        elif button_type == 'gesture gui':
            button = GestureDesignGUIButton(
                points_list=gesture_points_dict[str(index)]['point_list'],
                text=text,
                center_point=gesture_points_dict[str(index)]['pc'],
                num_points=gesture_points_dict['num_points'],
                hotkey=index,
                type_point=gesture_points_dict[str(index)]['pl']
            )
            # no idea why it's not setting with the pos being sent through...
            # so just using the post hack instead =\
            button.setPos(gesture_points_dict['pos'], gesture_points_dict['pos'])
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
        if 'hotkey' in button_type:
            self.button_list = [
                ['1', '2', '3', '4', '5'],
                ['q', 'w', 'e', 'r', 't'],
                ['a', 's', 'd', 'f', 'g'],
                ['z', 'x', 'c', 'v', 'b'],
            ]
        elif 'gesture' in button_type:
            self.button_list = [['0', '1', '2', '3', '4', '5', '6', '7']]

        for row in self.button_list:
            for item in row:
                unique_hash = None
                # create buttons that are not empty
                if '.' in file_dict[item]:
                    if '.py' in file_dict[item]:
                        unique_hash, name = file_dict[item][file_dict[item].rindex('/')+1:].replace('.py', '').split('.')
                    elif '.json' in file_dict[item]:
                        unique_hash, name = file_dict[item][file_dict[item].rindex('/')+1:].replace('.json', '').split('.')
                    if 'gesture' in button_type:
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
                    self.button_dict[item].setFilepath(file_dict[item])
                    if item_dict:
                        if file_dict[item] in list(item_dict.keys()):
                            self.button_dict[item].setItem(item_dict[file_dict[item]])
                            self.button_dict[item].setHash(unique_hash)
                    file_type = Locals().checkFileType(file_dict[item])

                    self.button_dict[item].setFileType(file_type=file_type)
                    self.button_dict[item].setButtonColor()

                # Create Empty Buttons
                # Will bypass for the gesture user display
                else:
                    if button_type != 'gesture gui':
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
                        self.button_dict[item].setButtonColor()

        self.setButtonSize()

    def updateButtons(self):
        """ Updates all of the buttons file paths """

        script_editor_widget = getWidgetAncestorByName(self, "AbstractScriptEditorWidget")
        item_dict = script_editor_widget.scriptWidget().itemDict()
        button_list = self.getButtonDict()
        for key in list(button_list.keys()):
            button = button_list[key]
            if hasattr(button, 'file_path'):
                if button.filepath():
                    item = item_dict[str(button.filepath())]
                    button.updateButton(current_item=item)

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
    """ Base class used for all Design Buttons (Gesture/Hotkey) """

    def __name__(self):
        return '__design_button_widget__'

    """ PROPERTIES """
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
        if not hasattr(self, 'file_type'):
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
                hotkey_dict[self.getHotkey()] = ''
            else:
                hotkey_dict[self.getHotkey()] = file_path

            # write out json
            design_path = self.getDesignPath()
            if file_path:
                # Writing JSON data
                with open(design_path, 'w') as f:
                    json.dump(hotkey_dict, f)

    def updateButton(self, current_item=None):
        if current_item:
            item_type = current_item.getItemType()
            dropable_list = ['script', 'gesture', 'hotkey']
            if item_type in dropable_list:
                if isinstance(self, GestureDesignEditorButton):
                    self.setText('%s' % (current_item.text(0)))
                elif isinstance(self, GestureDesignGUIButton):
                    self.setText('%s' % (current_item.text(0)))
                else:
                    self.setText(self.hotkey + '\n%s' % (current_item.text(0)))

                file_path = current_item.filepath()
                self.updateFile(file_path=file_path)

                self.setFilepath(file_path)

                self.setHash(current_item.getHash())
                self.setItem(current_item)
                if os.path.exists(file_path):
                    file_type = Locals().checkFileType(file_path)
                    self.setFileType(file_type)
                    self.setButtonColor()
                else:
                    self.updateButton(current_item=None)
        else:
            self.setText(self.getHotkey())
            delattr(self, 'hash')
            delattr(self, 'file_path')
            # delattr(self, 'item')
            delattr(self, 'file_type')
            self.setButtonColor()


class AbstractHotkeyDesignWidget(QWidget, AbstractDesignWidget):
    """ AbstractHotkeyDesignWidget base class"""
    def __init__(
        self,
        parent=None,
        item=None,
        file_path='',
        init_pos=None
    ):
        super(AbstractHotkeyDesignWidget, self).__init__(parent)

    def __name__(self):
        return '__hotkey_editor_widget__'

    def getButtonSize(self):
        width = self.geometry().width() / 5
        height = self.geometry().height() / 4
        return width, height

    """ EVENTS """

    def resizeEvent(self, *args, **kwargs):
        self.setButtonSize()
        return QWidget.resizeEvent(self, *args, **kwargs)


class AbstractHotkeyDesignButtonWidget(QPushButton, AbstractDesignButtonInterface):
    def __init__(self, parent=None, text=None, unique_hash=None):
        super(AbstractHotkeyDesignButtonWidget, self).__init__(parent)
        self.setText(text)
        self.setHotkey(text)
        self.setAcceptDrops(True)
        self.clicked.connect(self.execute)
        self.setHash(unique_hash)

    def setButtonColor(self):
        # needs to be updated...
        if hasattr(self, 'hotkey'):
            finger_list = {}
            finger_list['a'] = ['1', 'q', 'a', 'z']
            finger_list['s'] = ['2', 'w', 's', 'x']
            finger_list['d'] = ['3', 'e', 'd', 'c']
            finger_list['f'] = ['4', 'r', 'f', 'v']
            finger_list['g'] = ['5', 't', 'g', 'b']
            for finger in finger_list.keys():
                for item in finger_list[finger]:
                    hotkey = self.getHotkey()
                    color = 100
                    if hotkey in ['a', 's', 'd', 'f', 'g']:
                        color = color + (color * 2)
                        if color > 255:
                            color = 255
                    color = str(color)
                    style_sheet_list = []
                    style_sheet_list.append(
                        'border-style: dotted;\
                        border-width: 3px;\
                        border-radius: 0px;\
                        background-color: rgb(64,64,64);'
                    )

                    if hotkey in finger_list['a']:
                        style_sheet_list.append(
                            'border-color: rgb(%s,0,0);' % color
                        )
                        new_color = '(%s,0,0)' % str(float(color) * .75)
                    elif hotkey in finger_list['s']:
                        style_sheet_list.append(
                            'border-color: rgb(0,%s,0);' % color
                        )
                        new_color = '(0,%s,0)' % str(float(color) * .75)
                    elif hotkey in finger_list['d']:
                        style_sheet_list.append(
                            'border-color: rgb(0,0,%s);' % color
                        )
                        new_color = '(0,0,%s)' % str(float(color) * .75)
                    elif hotkey in finger_list['f']:
                        style_sheet_list.append(
                            'border-color: rgb(%s,%s,0);' % (color, color)
                        )
                        new_color = '(%s,%s,0)' % (
                            str(float(color) * .75), str(float(color) * .75)
                        )
                    elif hotkey in finger_list['g']:
                        style_sheet_list.append(
                            'border-color: rgb(%s,0,%s);' % (color, color)
                        )
                        new_color = '(%s,0,%s)' % (
                            str(float(color) * .75), str(float(color) * .75)
                        )
                    if hasattr(self, 'file_type'):
                        if self.getFileType() == 'hotkey':
                            style_sheet_list.append(
                                'border-style: double ;\
                                border-width: 6px;\
                                background-color: rgb(80,80,80);\
                                border-color: rgb%s;'
                                % new_color
                            )
                        elif self.getFileType() == 'script':
                            style_sheet_list.append(
                                'border-style: solid ;\
                                background-color: rgb(80,80,80);\
                                border-color: rgb%s;'
                                % new_color
                            )

                    self.setStyleSheet(''.join(style_sheet_list))


class GestureDesignWidget(QGraphicsView, AbstractDesignWidget):
    def __init__(
        self,
        parent=None,
        item=None,
        file_path='',
        init_pos=None,
        display_type=None,
        script_list=None,
        size=50
    ):
        super(GestureDesignWidget, self).__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalScrollBar().setStyleSheet('height:0px')
        self.verticalScrollBar().setStyleSheet('width:0px')

    def __name__(self):
        return '__gesture_editor_widget__'

    """ EVENTS"""

    def updatePolygons(
        self,
        num_points=8,
        display_type='gesture editor',
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
            # ===================================================================
            # inner right
            # ===================================================================
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

            # ===================================================================
            # Center Point of polygon
            # ===================================================================
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

            # ===================================================================
            # Add inner points to list for central button
            # ===================================================================
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

            # ===================================================================
            # Type Label
            # ===================================================================
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
        polygon_points_dict['num_points'] = num_points
        polygon_points_dict['pos'] = size * .5
        rc = (((r0 - r1) * .5) + r1)

        # create polygon segments
        for index in range(num_points):
            p0, p1, p2, p3, pc, p4, pl = getPoints(index, num_points, offset, r0, r1)
            points_list = [p0, p1, p3, p2, p0]
            polygon_points_dict[str(index)] = {}
            polygon_points_dict[str(index)]['point_list'] = points_list
            polygon_points_dict[str(index)]['pc'] = pc
            polygon_points_dict[str(index)]['pl'] = pl

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

    def setButtonColor(self):
        #self.label_item.setPlainText('None')

        pen = self.poly_item.pen()
        width = 2
        pen.setWidth(width)
        pen_style = Qt.CustomDashLine
        file_type = self.getFileType()
        # set up morse code dots...
        if file_type is None:
            text = 'None'
            color = QColor(0, 0, 0)

            morse_code = [
                3, 1, 1, 3,
                3, 1, 3, 1, 3, 3,
                3, 1, 1, 3,
                1, 7
            ]
        else:
            if file_type == 'hotkey':
                text = 'hotkey'
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
            elif file_type == 'gesture':
                text = 'gesture'
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
            elif file_type == 'script':
                text = 'script'
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
        #self.text_item.setDefaultTextColor(color)


class GestureDesignPolyWidget(QGraphicsPolygonItem, AbstractDesignButtonInterface):
    def __init__(self, parent=None, points_list=None):
        super(GestureDesignPolyWidget, self).__init__(parent)
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


""" HOTKEY WIDGETS """
class HotkeyDesignEditorWidget(AbstractHotkeyDesignWidget):
    """ Hotkey designer displayed as a widget in the DesignTab

    Displayed on right side when user clicks on a "HotkeyDesign" item
    The individual buttons inside of this are the HotkeyDesignEditorButtons
    """
    def __init__(self, parent=None, item=None, file_path=''):
        super(HotkeyDesignEditorWidget, self).__init__(parent)
        # set up default attributes
        self.setFilepath(file_path)
        # self.button_dict = {}
        file_dict = getJSONData(self.filepath())

        script_editor_widget = getWidgetAncestorByName(self.parentWidget(), "AbstractScriptEditorWidget")
        item_dict = script_editor_widget.scriptWidget().itemDict()
        self.item = item
        self.populate(file_dict, item_dict=item_dict, button_type='hotkey editor')

    def getButtonSize(self):
        width   = self.geometry().width() / 4
        height  = self.geometry().height() / 4 
        return width, height

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
        super(HotkeyDesignEditorButton, self).__init__(parent)
        self.setText(text)
        self.setHotkey(text)
        self.setAcceptDrops(True)
        #self.clicked.connect(self.execute)
        self.setHash(unique_hash)

    def __name__(self):
        return '__design_button__'

    def execute(self):
        if hasattr(self, 'item'):
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
        current_item = self.getCurrentItem()
        item_type = current_item.getItemType()
        dropable_list = ['script', 'gesture', 'hotkey']
        if item_type in dropable_list:
            event.accept()
        return QPushButton.dragEnterEvent(self, event, *args, **kwargs)

    def dropEvent(self, event, *args, **kwargs):
        self.updateButton(current_item=self.getCurrentItem())
        return QPushButton.dropEvent(self, event, *args, **kwargs)

    def mouseReleaseEvent(self, event, *args, **kwargs):
        if event.button() == Qt.MiddleButton:
            if hasattr(self, 'file_path'):
                self.updateFile(delete=True)
                self.updateButton()
        return QPushButton.mouseReleaseEvent(self, event, *args, **kwargs)


""" GESTURE WIDGETS """
class GestureDesignEditorWidget(GestureDesignWidget):
    def __init__(
        self,
        parent=None,
        item=None,
        file_path='',
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
            display_type='gesture editor',
            r0=outer_radius,
            r1=inner_radius,
            size=size,
            item_dict=item_dict,
            file_dict=file_dict
        )
        # set scene display
        self.setMaximumSize(size, size)

        file_dict = getJSONData(self.filepath())


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

        self.text_item = GestureDesignGUITextItem(
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

    def execute(self):
        if hasattr(self, 'item'):
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
        dropable_list = ['script', 'gesture', 'hotkey']
        if item_type in dropable_list:
            event.accept()

        return QGraphicsItemGroup.dragEnterEvent(self, event, *args, **kwargs)

    def dropEvent(self, event, *args, **kwargs):
        self.updateButton(current_item=self.getCurrentItem())
        return QGraphicsItemGroup.dropEvent(self, event, *args, **kwargs)

    def mousePressEvent(self, event, *args, **kwargs):
        if event.button() == Qt.MiddleButton:
            if hasattr(self, 'file_path'):
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

        
        if self.hotkey in '123':
            ypos -= 20
        elif self.hotkey in '567':
            ypos += 20
        elif self.hotkey == '0':
            xpos -= 15
        elif self.hotkey == '4':
            xpos += 15
        
        # specific handlers to center based on awkward shapes...
        new_pos = QPointF(xpos, ypos)
        self.setPos(new_pos)


class GestureDesignGUIWidget(GestureDesignWidget):
    def __init__(
        self,
        parent=None,
        file_path='',
        init_pos=None,
        size=None
    ):
        super(GestureDesignGUIWidget, self).__init__(parent)
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
            display_type='gesture gui',
            r0=outer_radius,
            r1=inner_radius,
            size=size,
            file_dict=file_dict
        )

        # set scene display
        self.setMaximumSize(size*5, size*5)


class GestureDesignGUIButton(GestureDesignButtonWidget):
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
        super(GestureDesignGUIButton, self).__init__(parent)
        # set up items
        self.poly_item = GestureDesignPolyWidget(points_list=points_list)

        self.text_item = GestureDesignGUITextItem(
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
        if self.getFileType() == 'script':
            if os.path.exists(self.filepath()):
                with open(self.filepath()) as script_descriptor:
                    print('execute gesture')
                    exec(compile(script_descriptor.read(), "script_descriptor", "exec"))
        elif self.getFileType() == 'hotkey':
            # katana_main = UI4.App.MainWindow.GetMainWindow()
            pos = QCursor.pos()
            popup_menu_widget = PopupHotkeyMenu(file_path=self.filepath(), pos=pos)
            popup_menu_widget.show()
        elif self.getFileType() == 'gesture':
            # katana_main = UI4.App.MainWindow.GetMainWindow()
            popup_gesture_widget = PopupGestureMenu(file_path=self.filepath())
            popup_gesture_widget.show()

        self.scene().views()[0].parent().close()

    def hoverEnterEvent(self, *args, **kwargs):
        if hasattr(self, 'file_path'):
            self.execute()
        return GestureDesignButtonWidget.hoverEnterEvent(self, *args, **kwargs)


class GestureDesignGUITextItem(QGraphicsTextItem):
    def __init__(
        self,
        parent=None,
        text=None,
        hotkey=None,
        pos=None
    ):

        super(GestureDesignGUITextItem, self).__init__(parent)
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
        if self.hotkey in '26':
            xpos = pos.x() - (width * .5)
            text_format.setAlignment(Qt.AlignCenter)
        # right
        elif self.hotkey in '107':
            xpos = pos.x()
            text_format.setAlignment(Qt.AlignRight)
            pass #align right
        # left
        elif self.hotkey in '345':
            xpos = pos.x() - (width)
            text_format.setAlignment(Qt.AlignLeft)
        cursor = self.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(text_format)
        cursor.clearSelection()
        self.setTextCursor(cursor)

        ypos = pos.y() - 15

        """
        if self.hotkey in '123':
            ypos -= 20
        elif self.hotkey in '567':
            ypos += 20
        elif self.hotkey == '0':
            xpos -= 15
        elif self.hotkey == '4':
            xpos += 15
        """
        # specific handlers to center based on awkward shapes...
        new_pos = QPointF(xpos, ypos)
        self.setPos(new_pos)


""" POPUP MENUS """
class HotkeyDesignPopupWidget(AbstractHotkeyDesignWidget):
    def __init__(self, parent=None, item=None, file_path='', init_pos=None):
        super(HotkeyDesignPopupWidget, self).__init__(parent)
        # set up default attributes
        self.setFilepath(file_path)
        self.button_dict = {}
        file_dict = getJSONData(self.filepath())

        self.init_pos = init_pos
        self.populate(file_dict, button_type='hotkey gui')

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
        super(HotkeyDesignPopupButton, self).__init__(parent)
        self.setText(text)
        self.setHotkey(text)
        self.setAcceptDrops(True)
        self.clicked.connect(self.execute)
        self.setHash(unique_hash)

    def execute(self):
        if self.getFileType() == 'script':
            if os.path.exists(self.filepath()):
                with open(self.filepath()) as script_descriptor:
                    exec(compile(script_descriptor.read(), "script_descriptor", "exec"))
        elif self.getFileType() == 'hotkey':
            self.showHotkeyDesign(self.filepath())
        elif self.getFileType() == 'gesture':
            gesture_menu = PopupGestureMenu(self, file_path=self.filepath())
            gesture_menu.show()

        getWidgetAncestor(self, PopupHotkeyMenu).close()

    def showHotkeyDesign(self, file_path):
        pos = self.parentWidget().init_pos
        popup_hotkey_menu = PopupHotkeyMenu(self, file_path=file_path, pos=pos)
        popup_hotkey_menu.show()


class PopupHotkeyMenu(QWidget):
    """ Popup Hotkey Menu

    Attributes:
        popup_stack (list): of strings of the current paths that the user
            has clicked to get to the current menu"""
    def __init__(self, parent=None, file_path=None, pos=None, size=QSize(1800, 600)):
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
        painter.setOpacity(0.5)
        bg_color = QColor(32, 32, 32, 255)
        painter.setBrush(bg_color)
        painter.setPen(QPen(bg_color))
        painter.drawRect(self.window().rect())

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
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        design_widget = GestureDesignGUIWidget(self, file_path=file_path, init_pos=pos, size=size)
        main_layout.addWidget(design_widget)

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
