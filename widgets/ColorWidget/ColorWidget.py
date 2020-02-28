import sys
import math
import re

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *

from cgqtpy.delegates import LadderDelegate

'''
KATANA BUGS:
    - Drag outside...
        - Hitbox is not correct, skewed by what appears to be the
            border-width to the topleft
IDEA:
    Put ring of default colors around the color widget for quick color selection

'''


class ColorWidget(QWidget):
    '''
    @attr: <str> katana attribute to adjust
    @color: <str> rgb '0.8 0.8 0.8'
    @main_widget: primary widget to get modules from
    @widget_default_data: <dict> dictionary of default attributes
        'default_value': '0.800000011921 0.800000011921 0.800000011921',
        'name': 'color',
        'data_type': 'color',
        'is_array': '0',
        'attr_name': '',
        'attr_loc': 'material.dlSurfaceParams.color'
    '''
    def __init__(
                self,
                parent=None,
                attr=None,
                color='.5 0.18 0.18',
                #main_widget=None,
                widget_default_data=None
                ):
        super(ColorWidget, self).__init__(parent)
        main_layout = QGridLayout()
        #self.main_widget = main_widget

        self.widget_default_data = widget_default_data
        self.attr = attr
        self.setLayout(main_layout)
        self.display_color_widget = ColorDisplayWidget(parent=self, main_widget=self)
        self.display_color_label = self.display_color_widget.color_label
        self.display_color_picker = self.display_color_widget.color_picker

        #  ----------------------------------------------- setup colors
        rgb_list = [float(value) for value in color.split(' ') if value != '']
        color = QColor()
        color.setRgb(rgb_list[0]*255, rgb_list[1]*255, rgb_list[2]*255)
        #self.setColor(color)
        #  ----------------------------------------------- setup rgb
        self.rgb_layout = QHBoxLayout()
        self.rgb_layout.setSpacing(SETTINGS.PADDING * 2)
        for count, value in enumerate(rgb_list):
            widget = ColorLabel(main_widget=self, value=value, channel=count)

            self.rgb_layout.addWidget(widget)
        #  ----------------------------------------------- setup HSV
        self.hsv_layout = QHBoxLayout()
        self.hsv_layout.setSpacing(0)
        hsv = self.getColor()
        hsv_list = [hsv.hue()/359, hsv.saturation()/255, hsv.value()/255]
        # setup gradient
        self.display_color_picker.scene.setupGradient(
            value=hsv.value(),
            sat=hsv.saturation()
        )
        for count, value in enumerate(hsv_list):
            group_box = HSVGroupBox(parent=self)
            if count == 0:
                group_box.setTitle('H')
            elif count == 1:
                group_box.setTitle('S')
            elif count == 2:
                group_box.setTitle('V')
            widget = HSVLabel(main_widget=self, value=value, channel=count)

            group_box.layout().addWidget(widget)
            self.hsv_layout.addWidget(group_box)

        # setup layouts
        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.display_color_widget)
        self.stacked_layout.setCurrentIndex(0)

        main_layout.addLayout(self.stacked_layout, 0, 0, 1, 1)
        main_layout.addLayout(self.rgb_layout, 1, 0, 1, 1)
        main_layout.addLayout(self.hsv_layout, 2, 0, 1, 1)

        self.setColor(color)
        self.setStyleSheet(
            "QLineEdit { background-color: rgba(0,0,0,0);\
            qproperty-cursorPosition: 0; }"
        )

    def __name__(self):
        return 'color'

    def updateFromStr(self, color):
        '''
        @color <str> color strf 'r g b'
        '''
        red, green, blue = color.split(' ')
        color = QColor()
        color.setRgb(
            255 * float(red),
            255 * float(green),
            255 * float(blue)
        )
        self.setColor(color)
        self.updateRGB()
        self.updateHSV()

    def updateRGB(self):
        #  =====================================================
        # sets the text displayed to the user of the RGB labels
        #  =====================================================
        if hasattr(self, 'rgb_layout'):
            try:
                red = '%.4g' % float(self.getColor().red() / 255)
                green = '%.4g' % float(self.getColor().green() / 255)
                blue = '%.4g' % float(self.getColor().blue() / 255)
                self.rgb_layout.itemAt(0).widget().setValue(str(red), update=False)
                self.rgb_layout.itemAt(1).widget().setValue(str(green), update=False)
                self.rgb_layout.itemAt(2).widget().setValue(str(blue), update=False)
            except:
                # this is me being lazy, lol
                pass

    def updateHSV(self):
        #  =====================================================
        # sets the text displayed to the user of the HSV labels
        #  =====================================================
        if hasattr(self, 'hsv_layout'):
            color = self.getColor()
            hue = '%.4g' % float(color.hue() / 359)
            sat = '%.4g' % float(color.saturation() / 255)
            val = '%.4g' % float(color.value() / 255)

            # sorry this is kinda nasty... I really should do something not as crappy...
            self.hsv_layout.itemAt(0).widget().layout().itemAt(0).widget().setValue(str(hue), update=False)
            self.hsv_layout.itemAt(1).widget().layout().itemAt(0).widget().setValue(str(sat), update=False)
            self.hsv_layout.itemAt(2).widget().layout().itemAt(0).widget().setValue(str(val), update=False)

    def setColor(self, color):
        '''
        @color <QColor>
        sets the color of the label on top of the color selector,
        this will also update the HSV/RGB boxes aswell
        '''
        #  =====================================================
        # sets the color, this sends a signal to the main widget to set the
        # value of the color on the actual opscript.  So that it will actually
        # set the new attr value
        # @color is a string with space seperation
        #  =====================================================
        self.color = color
        if hasattr(self, 'display_color_widget'):
            red = self.getColor().red()
            green = self.getColor().green()
            blue = self.getColor().blue()
            self.display_color_widget.setStyleSheet(
                'border-style: solid; \
                border-width: %spx; \
                border-color: rgba(%s, %s, %s, 255);'
                % (SETTINGS.PADDING, red, green, blue)
            )
            value = '%s %s %s' % (red, green, blue)
            '''
            self.main_widget.setValue(
                attr=self.attr,
                value=value,
                widget_default_data=self.widget_default_data
                )
            '''

    def getColor(self):
        if not hasattr(self, 'color'):
            self.color = QColor()
        return self.color


class DataTypeLineEdit(QLineEdit):
    def __init__(
            self,
            parent=None,
            data_type=None,
            domath=False,
            allownegative=False
        ):

        super(DataTypeLineEdit, self).__init__(parent)
        self.setAllowNegative(allownegative)
        self.setDoMath(domath)
        self.setDataType(data_type)
        self.editingFinished.connect(self.finishUserInput)
        self.setAlignment(Qt.AlignCenter)

    def home(self, *args, **kwargs):
        print('home')
        #return QLineEdit.home(self, *args, **kwargs)

    ''' PROPERTIES '''
    def setAllowNegative(self, boolean):
        self.allow_negative = boolean

    def getAllowNegative(self):
        return self.allow_negative

    def setDoMath(self, domath):
        self.domath = domath

    def getDoMath(self):
        return self.domath

    def getDataType(self):
        return self.data_type

    def setDataType(self, data_type):
        self.data_type = data_type
        # SET UP KEY LIST
        self.key_list = []
        number_types = ['float', 'number', 'color', 'int']
        if data_type in number_types:
            self.key_list = [
                                Qt.Key_0,
                                Qt.Key_1,
                                Qt.Key_2,
                                Qt.Key_3,
                                Qt.Key_4,
                                Qt.Key_5,
                                Qt.Key_6,
                                Qt.Key_7,
                                Qt.Key_8,
                                Qt.Key_9,
                                Qt.Key_Left,
                                Qt.Key_Right,
                                Qt.Key_Up,
                                Qt.Key_Down,
                                Qt.Key_Delete,
                                Qt.Key_Backspace,
                                Qt.Key_Return,
                                Qt.Key_Enter,
                                Qt.Key_CapsLock
                                ]
        if data_type == 'float':
            self.key_list.append(Qt.Key_Period)
        if data_type == 'color':
            self.key_list.append(Qt.Key_Period)
            self.key_list.append(Qt.Key_Space)
        if self.getDoMath() is True:
            math_keys = [
                Qt.Key_V,
                Qt.Key_Plus,
                Qt.Key_plusminus,
                Qt.Key_Minus,
                Qt.Key_multiply,
                Qt.Key_Asterisk,
                Qt.Key_Slash
            ]
            for key in math_keys:
                self.key_list.append(key)
        if self.getAllowNegative() is True:
            self.key_list.append(Qt.Key_Minus)

    def setOrigValue(self, value):
        self.orig_value = value

    def getOrigValue(self):
        return self.orig_value

    ''' SIGNALS / EVENTS '''
    def focusInEvent(self, *args, **kwargs):
        self.setOrigValue(self.text())
        return QLineEdit.focusInEvent(self, *args, **kwargs)

    def finishUserInput(self):
        data_type = self.getDataType()
        text = self.text()
        orig_value = self.getOrigValue()

        # =======================================================================
        # Validate user input
        # =======================================================================
        if data_type == 'float':
            try:
                float(self.text())
            except:
                self.setText(orig_value)

        elif data_type == 'int':
            try:
                float(self.text())
            except:
                self.setText(orig_value)

        elif data_type == 'color':
            try:
                rgb = filter(None, text.split(' '))
                if len(rgb) != 3:
                    self.setText(orig_value)
                    return
                else:
                    for value in rgb:
                        float(value)

            except:
                self.setText(orig_value)
            pass

    def mousePressEvent(self, event, *args, **kwargs):
        if event.button() == Qt.MiddleButton:
            return
        return QLineEdit.mousePressEvent(self, event, *args, **kwargs)

    def keyPressEvent(self, event, *args, **kwargs):
        if event.key() in self.key_list:
            return QLineEdit.keyPressEvent(self, event, *args, **kwargs)
        elif self.getDataType() == 'string':
            return QLineEdit.keyPressEvent(self, event, *args, **kwargs)


class ValueLabel(DataTypeLineEdit):
    #  ==========================================================================
    #  abstract label to be used by the Color/HSV labels to inherit
    #  ==========================================================================
    def __init__(
            self,
            parent=None,
            main_widget=None,
            value=0,
            channel=None
            ):
        super(ValueLabel, self).__init__(parent=parent)
        self.value = value
        self.setDataType('float')
        '''
        self.setStyleSheet(
            'background-color: rgba(0,0,0,0);\
            qproperty-cursorPosition: 0;'
            )
        '''
        self.setAlignment(Qt.AlignLeft)
        #self.home(False)

    def __name__(self):
        return 'valuelabel'

    def setValue(self, value=None, update=True, offset=None):
        '''
        @value float rgb color (single channel)
        @update determines whether or not this will set the
            property or update the property as well
        @offset <float> how much the value should be offset
            this is primarily used with ladder widgets.  If it is set
            to None, it will just use the 'value' arg coming in
        '''
        # =======================================================================
        # Add offset (if applicable)
        # =======================================================================
        if offset:
            value = eval('+'.join([str(self.value), str(offset)]))
        # =======================================================================
        # make sure values are legal
        # =======================================================================
        if float(value) > 1:
            value = 1
        elif float(value) < 0:
            value = 0

        # =======================================================================
        # is offset
        # =======================================================================
        self.value = value
        self.setText(str(self.value))

        # =======================================================================
        # update
        # =======================================================================
        if update is True:
            old_color = self.main_widget.getColor()
            # RGB Updated
            if self.__name__() == 'colorlabel':
                red = old_color.red()
                green = old_color.green()
                blue = old_color.blue()
                if self.channel == 0:
                    red = value * 255
                elif self.channel == 1:
                    green = value * 255
                elif self.channel == 2:
                    blue = value * 255

                color = QColor()
                color.setRgb(red, green, blue)
                self.main_widget.setColor(color)
                self.main_widget.updateHSV()
                if hasattr(self, 'setColor'):
                    self.setColor(value)

            # HSV Updated
            elif self.__name__() == 'hsvlabel':
                hue = old_color.hue()
                sat = old_color.saturation()
                val = old_color.value()

                if self.channel == 0:
                    hue = value * 360
                elif self.channel == 1:
                    sat = value * 255
                elif self.channel == 2:
                    val = value * 255
                color = QColor()
                color.setHsv(hue, sat, val)
                self.main_widget.setColor(color)

                self.main_widget.updateRGB()

            # update the color picker here...
            huef = color.hueF()
            valuef = color.valueF()
            scene = self.main_widget.display_color_picker.scene
            xpos = (huef * scene.width())
            ypos = math.fabs((valuef * scene.height()) - scene.height())

            pos = QPoint(xpos, ypos)
            scene.updateCrosshair(pos)

            # update color picker gradient
            value = color.value()
            scene.setupGradient(
                value=value,
                sat=color.saturation()
            )

    def getValue(self):
        return self.value

    def setPos(self, pos):
        self.mouse_pos = pos

    def getPos(self):
        return self.mouse_pos

    def mousePressEvent(self, event, *args, **kwargs):
        if event.button() == Qt.MiddleButton:
            value_list = [0.0001, 0.001, 0.01, 0.1]
            pos = QCursor.pos()

            ladder = LadderDelegate(
                parent=self,
                widget=self,
                pos=pos,
                value_list=value_list
            )
            ladder.show()
            self.setPos(event.pos().x())
            return
        return QLineEdit.mousePressEvent(self, event, *args, **kwargs)


class ColorLabel(ValueLabel):
    def __init__(
            self,
            parent=None,
            main_widget=None,
            value=None,
            channel=None
            ):

        super(ColorLabel, self).__init__(parent=parent)
        self.main_widget = main_widget
        self.channel = channel
        self.setValue(value, update=False)
        self.setText(str(value))
        self.setColor(value)
        self.editingFinished.connect(self.userInput)

    def __name__(self):
        return 'colorlabel'

    def setColor(self, value):
        '''
        @value colorf
        updates the background color of the widget
        '''
        value = value * 255
        if self.channel == 0:
            self.setStyleSheet(
                'border-color:rgb(%s,0,0); \
                border-width: 1px; \
                border-style: solid; \
                border-radius: %spx;\
                background-color: rgba(%s) ;\
                ' % (
                    value, SETTINGS.PADDING * 2,
                    SETTINGS.DARK_TRANSPARENT_STRRGBA
                )
            )
        elif self.channel == 1:
            self.setStyleSheet(
                'border-color:rgb(0, %s, 0); \
                border-width: 1px; \
                border-style: solid; \
                border-radius: %spx;\
                background-color: rgba(%s) ;\
                ' % (
                    value, SETTINGS.PADDING * 2,
                    SETTINGS.DARK_TRANSPARENT_STRRGBA
                )
            )
        elif self.channel == 2:
            self.setStyleSheet(
                'border-color:rgb(0, 0, %s); \
                border-width: 1px; \
                border-style: solid; \
                border-radius: %spx;\
                background-color: rgba(%s) ;\
                ' % (
                    value, SETTINGS.PADDING * 2,
                    SETTINGS.DARK_TRANSPARENT_STRRGBA
                )
            )

    def userInput(self):
        value = self.text()
        self.setValue(float(value))


class HSVGroupBox(QGroupBox):
    def __init__(self, parent=None):
        super(HSVGroupBox, self).__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, SETTINGS.PADDING * 3, 0, 0)
        self.setLayout(layout)
        self.setStyleSheet(SETTINGS.GROUP_BOX_SS)


class HSVLabel(ValueLabel):
    def __init__(self, parent=None,
                 main_widget=None,
                 value=None,
                 channel=None):
        super(HSVLabel, self).__init__(parent=parent)
        self.main_widget = main_widget
        self.channel = channel
        self.setValue(value, update=False)
        self.setText(str(value))
        self.editingFinished.connect(self.userInput)

    def __name__(self):
        return 'hsvlabel'

    def userInput(self):
        value = self.text()
        self.setValue(float(value))


class ColorDisplayWidget(QWidget):
    #  ==========================================================================
    # Display color swatch to the user
    #  ==========================================================================
    def __init__(self, parent=None, main_widget=None):
        super(ColorDisplayWidget, self).__init__(parent=parent)
        self.main_widget = main_widget
        layout = QStackedLayout()
        self.setLayout(layout)
        self.color_picker = ColorPickerWidget(main_widget=main_widget)
        # not using this any more... and was to lazy to remove...
        # self.color_label --> ColorDisplayLabel lol
        self.color_label = ColorDisplayLabel(main_widget=main_widget)
        layout.addWidget(self.color_label)
        layout.addWidget(self.color_picker)


class ColorPickerWidget(QWidget):
    '''
    MainWindow
        --> Layout
            --> GraphicsView (GLWidget)
                --> GraphicsScene
    '''
    def __init__(self, parent=None, main_widget=None):
        super(ColorPickerWidget, self).__init__(parent)
        # =======================================================================
        # setup main widget
        # =======================================================================
        self.main_widget = main_widget
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.scene = ColorGraphicsScene()
        self.view = ColorGraphicsView(self.scene, main_widget=self)

        layout.addWidget(self.view)

    def mousePressEvent(self, *args, **kwargs):
        return QWidget.mousePressEvent(self, *args, **kwargs)

    def getColor(self):
        return self.main_widget.getColor()

    def updateColor(self, color):
        self.main_widget.setColor(color)
        self.main_widget.updateRGB()
        self.main_widget.updateHSV()

    def leaveEvent(self, *args, **kwargs):
        self.parent().layout().setCurrentIndex(0)
        return QWidget.leaveEvent(self, *args, **kwargs)


class ColorGraphicsView(QGraphicsView):
    '''
    @previous_size: <geometry> hold the previous position
        so that a resize event can recalculate the cross hair
        based off of this geometry
    '''
    def __init__(self, parent=None, main_widget=None):
        super(ColorGraphicsView, self).__init__(parent)
        self.main_widget = main_widget
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def mousePressEvent(self, *args, **kwargs):
        self._picking = True
        self._in_color_widget = True
        self.setCursor(Qt.BlankCursor)

        return QGraphicsView.mousePressEvent(self, *args, **kwargs)

    def mouseMoveEvent(self, event, *args, **kwargs):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.AltModifier:
            return

        if self._picking:
            # ===================================================================
            # get color
            # ===================================================================
            scene = self.scene()
            pos = event.globalPos()
            self._pickColor(pos)
            scene.updateCrosshair(event.pos())

            # check mouse position...
            top_left = self.mapToGlobal(self.pos())
            top = top_left.y()
            left = top_left.x()
            right = left + self.geometry().width()
            bot = top + self.geometry().height()
            if pos.y() < top or pos.y() > bot or pos.x() < left or pos.x() > right:
                if self._in_color_widget == True:
                    self.setCursor(Qt.CrossCursor)
                    self._in_color_widget = False
            else:
                if self._in_color_widget == False:
                    self.setCursor(Qt.BlankCursor)
                    self._in_color_widget = True

        return QGraphicsView.mouseMoveEvent(self, event, *args, **kwargs)

    def mouseReleaseEvent(self, *args, **kwargs):
        self._picking = False
        self.unsetCursor()
        return QGraphicsView.mouseReleaseEvent(self, *args, **kwargs)

    def _pickColor(self, pos):
        desktop = QApplication.desktop().winId()
        screen = QApplication.primaryScreen()
        pixmap = screen.grabWindow(
            desktop,
            pos.x(), pos.y(),
            1, 1
        )
        img = pixmap.toImage()
        color = QColor(img.pixel(0, 0))

        # might want to check here to make sure it's not grabbing black?
        self.main_widget.updateColor(color)

    def setPreviousSize(self, geometry):
        self.previous_size = geometry

    def getPreviousSize(self):
        if not hasattr(self, 'previous_size'):
            self.previous_size = self.geometry()
        return self.previous_size

    def resizeEvent(self, *args, **kwargs):
        '''
        allow widget to resize with the rectangle...
        '''
        # there has to be a better way to set this...

        # =======================================================================
        # resize widget
        # =======================================================================
        rect = self.geometry()
        self.scene().setSceneRect(
            rect.topLeft().x(),
            rect.topLeft().y(),
            rect.width(),
            rect.height()
        )

        # =======================================================================
        # update items
        # =======================================================================
        # gradient
        value = self.main_widget.getColor().value()
        sat = self.main_widget.getColor().saturation()
        self.scene().setupGradient(
            value=value,
            sat=sat
        )
        # crosshair
        # get normalized crosshair position
        crosshair_pos = self.scene().getCrosshairPos()
        old_width = self.getPreviousSize().width()
        old_height = self.getPreviousSize().height()
        crosshair_xpos = crosshair_pos.x() / old_width
        crosshair_ypos = crosshair_pos.y() / old_height

        # get new crosshair position
        xpos = crosshair_xpos * rect.width()
        ypos = crosshair_ypos * rect.height()
        new_pos = QPoint(xpos, ypos)
        self.scene().updateCrosshair(new_pos)

        self.setPreviousSize(rect)
        return QGraphicsView.resizeEvent(self, *args, **kwargs)


class ColorGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(ColorGraphicsScene, self).__init__(parent)
        self.CROSSHAIR_RADIUS = 10
        self.setSceneRect(0, 0, 500, 500)
        self.setupGradient()

        self.vlinetop_item = LineSegment()
        self.vlinetop_item.setLine(0, 0, 0, self.height())
        self.vlinebot_item = LineSegment()
        self.vlinebot_item.setLine(0, 0, 0, self.height())

        self.hlinetop_item = LineSegment()
        self.hlinetop_item.setLine(0, 0, self.width(), 0)
        self.hlinebot_item = LineSegment()
        self.hlinebot_item.setLine(0, 0, self.width(), 0)

        self.crosshair_circle = QGraphicsEllipseItem()
        self.crosshair_circle.setRect(
            -(self.CROSSHAIR_RADIUS*.5),
            -(self.CROSSHAIR_RADIUS*.5),
            self.CROSSHAIR_RADIUS,
            self.CROSSHAIR_RADIUS
        )

        # add items
        self.addItem(self.crosshair_circle)
        self.addItem(self.vlinetop_item)
        self.addItem(self.vlinebot_item)
        self.addItem(self.hlinetop_item)
        self.addItem(self.hlinebot_item)

    def getCrosshairPos(self):
        if not hasattr(self, 'crosshair_pos'):
            self.crosshair_pos = QPoint(0, 0)
        return self.crosshair_pos

    def setCrosshairPos(self, pos):
        self.crosshair_pos = pos

    def updateCrosshair(self, pos):
        '''
        @pos: <QPoint> new position to set the cross hair to
        '''
        crosshair_radius = self.CROSSHAIR_RADIUS * .5
        xpos = pos.x()
        ypos = pos.y()

        # update items positions
        self.crosshair_circle.setPos(pos)
        self.vlinetop_item.setLine(xpos, 0, xpos, ypos - crosshair_radius)
        self.vlinebot_item.setLine(xpos, ypos + crosshair_radius, xpos, self.height())
        self.hlinetop_item.setLine(0, ypos, xpos - crosshair_radius, ypos)
        self.hlinebot_item.setLine(xpos + crosshair_radius, ypos, self.width(), ypos)

        self.setCrosshairPos(pos)

    def setupGradient(self, value=None, sat=None):
        '''
        draws the background color square for the main widget
        '''
        if not value:
            value = 255
        if not sat:
            sat = 255
        sat = 255  # overriding sat here explicitely, because I don't like it
                        # its causing issues with the color picker for obvious reasons
        colorGradient = QLinearGradient(0, 0, self.width(), 0)

        num_colors = 6
        colorGradient.setSpread(QGradient.RepeatSpread)
        for x in range(num_colors):
            pos = (1 / num_colors) * (x)
            color = QColor()
            color.setHsv(x * (360/num_colors), sat, value)
            colorGradient.setColorAt(pos, color)
        # set red to end
        color = QColor()
        color.setHsv(0, sat, value)
        colorGradient.setColorAt(1, color)

        blackGradient = QLinearGradient(0, 0, 0, self.height())
        blackGradient.setSpread(QGradient.RepeatSpread)
        blackGradient.setColorAt(0, QColor(0, 0, 0, 0))
        blackGradient.setColorAt(1, QColor(value, value, value, 255))

        colorGradiantBrush = QBrush(colorGradient)
        blackGradiantBrush = QBrush(blackGradient)
        self.setBackgroundBrush(colorGradiantBrush)
        self.setForegroundBrush(blackGradiantBrush)

    def setItemPosition(self, item, x, y):
        point = QPointF(x, y)
        point_item = item.mapFromScene(point)
        item.setPos(point_item)


class LineSegment(QGraphicsLineItem):
    def __init__(self, parent=None):
        super(LineSegment, self).__init__(parent)
        pen = self.pen()
        pen.setWidth(1)
        self.setPen(pen)


class ColorDisplayLabel(QLabel):
    #  ==========================================================================
    # Display color swatch to the user
    #  ==========================================================================
    def __init__(self, parent=None, main_widget=None):
        super(ColorDisplayLabel, self).__init__(parent=parent)
        self.main_widget = main_widget
        self.setStyleSheet(
            'background-color: rgba(%s); color: rgb(200,200,64)'
            % SETTINGS.DARK_TRANSPARENT_STRRGBA
        )
        #self.setText('I\'m positive I just lost an electron. \n Better keep an ion that.')
        #self.setAlignment(Qt.AlignCenter)

    def enterEvent(self, *args, **kwargs):
        self.parent().layout().setCurrentIndex(1)
        return QLabel.enterEvent(self, *args, **kwargs)


class DefaultColorWidget(QWidget):
    def __init__(self, parent=None, default_widget=None):
        super(DefaultColorWidget, self).__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.color_widget = ColorWidget(main_widget=default_widget)
        layout.addWidget(self.color_widget)


class SETTINGS(object):
    GRID_SIZE = 50
    GRID_BORDER_WIDTH = 3
    HUD_BORDER_WIDTH = 1
    HUD_BORDER_OFFSET = 3
    PADDING = 3
    ALPHA = '48'
    CREATE_LABEL_WIDTH = 150
    SELECTION_WIDTH = 15

    # ===============================================================================
    # COLORS
    # ===============================================================================
    #Darkest (letters)
    DARK_GREEN_ORIG = '.01600 .16827 .03560'

    DARK_GREEN_RGB = QColor()
    #DARK_GREEN_RGB.setRgbF(.016 * 255, .16827 * 255, .03560 * 255)
    DARK_GREEN_RGB.setRgb(18, 86, 36)

    DARK_GREEN_STRI = '16, 86, 36'
    DARK_GREEN_STRRGBA = '16, 86, 36, 255'
    #DARK_GREEN_STRI = '8, 86, 18'

    DARK_GREEN_HSV = QColor()
    DARK_GREEN_HSV.setHsvF(.5, .9, .17)

    MID_GREEN_STRRGBA = '64, 128, 64, 255'

    LIGHT_GREEN_RGB = QColor()
    #LIGHT_GREEN_RGB.setRgb(10.08525, 95.9463, 20.9814)
    LIGHT_GREEN_RGB.setRgb(90, 180, 90)
    LIGHT_GREEN_STRRGBA = '90, 180, 90, 255'

    DARK_RED_RGB = QColor()
    DARK_RED_RGB.setRgb(86, 18, 36)

    LOCAL_YELLOW_STRRGBA = '240, 200, 0, 255'
    DARK_YELLOW_STRRGBA = '112, 112, 0, 255'

    DARK_GRAY_STRRGBA = '64, 64, 64, 255'

    FULL_TRANSPARENT_STRRGBA = '0, 0, 0, 0'
    DARK_TRANSPARENT_STRRGBA ='0, 0, 0, 48'
    LIGHT_TRANSPARENT_STRRGBA ='255, 255, 255, 12'

    # ===============================================================================
    # STYLE SHEETS
    # ===============================================================================
    BUTTON_SELECTED = \
        'border-width: 2px; \
        border-color: rgba(%s) ; \
        border-style: solid' \
        % LOCAL_YELLOW_STRRGBA

    BUTTON_DEFAULT = \
        'border-width: 1px; \
        border-color: rgba(%s) ; \
        border-style: solid' \
        % DARK_GRAY_STRRGBA

    TOOLTIP = 'QToolTip{ \
                        background-color: rgb(%s); \
                        color: rgb(%s); \
                        border: black solid 1px\
                    } \
                    ' % (DARK_GRAY_STRRGBA,             # Tool Tip BG
                        LOCAL_YELLOW_STRRGBA)      # Tool Tip Color

    # GROUP_BOX_HUD_WIDGET
    GROUP_BOX_HUD_WIDGET = \
        'QGroupBox{\
            background-color: rgba(0,0,0,%s);\
            border-width: %spx; \
            border-radius: %spx;\
            border-style: solid; \
            border-color: rgba(%s); \
        } \
        ' % (
            ALPHA,
            GRID_BORDER_WIDTH,                               # border-width
            PADDING * 2,                           # border-radius
            DARK_GREEN_STRRGBA,        # border color
        )
    '''
    QListView::item:selected:active {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #6a6ea9, stop: 1 #888dd9);
    }
    '''
    # FLOATING WIDGET
    FLOATING_LISTWIDGET_SS = \
        'QListView::item:hover{\
        color: rgba(%s);\
        }\
        QListView{\
        background-color: rgba(%s); \
        selection-color: rgba(%s);\
        selection-background-color: rgba(%s);\
        } ' % (
            LIGHT_GREEN_STRRGBA,
            FULL_TRANSPARENT_STRRGBA,
            LOCAL_YELLOW_STRRGBA,
            FULL_TRANSPARENT_STRRGBA,
        )
    FLOATING_LISTWIDGETHUD_SS = \
        'QListView::item:hover{\
        color: rgba(%s);\
        }\
        QListView{\
        background-color: rgba(%s); \
        selection-color: rgba(%s);\
        selection-background-color: rgba(%s);\
        } ' % (
            LIGHT_GREEN_STRRGBA,
            DARK_TRANSPARENT_STRRGBA,
            LOCAL_YELLOW_STRRGBA,
            FULL_TRANSPARENT_STRRGBA,
        )

    FLOATING_WIDGET_HUD_SS =\
        'QWidget.UserHUD{background-color: rgba(0,0,0,0); \
        border-width: %spx; \
        border-style: solid; \
        border-color: rgba(%s);} \
        ' % (
            HUD_BORDER_WIDTH,
            DARK_GREEN_STRRGBA
        )
    # ===============================================================================
    # GROUP BOX MASTER STYLE SHEET
    # ===============================================================================

    # REGEX
    background_color = r"background-color: .*?(?=\))"
    border_radius = r"border-width: .*?(?=p)"
    border_color = r"border-color: rgba\(.*?(?=\))"
    color = r"color: rgba\(.*?(?=\))"

    # MASTER
    GROUP_BOX_SS = \
        'QGroupBox::title{\
        subcontrol-origin: margin;\
        subcontrol-position: top center; \
        padding: -%spx %spx; \
        } \
        QGroupBox{\
            background-color: rgba(0,0,0,%s);\
            border-width: %spx; \
            border-radius: %spx;\
            border-style: solid; \
            border-color: rgba(%s); \
            margin-top: 1ex;\
            margin-bottom: %s;\
            margin-left: %s;\
            margin-right: %s;\
        } \
        %s \
        ' % (
            PADDING,                               # padding text height
            PADDING * 2,                       # padding offset
            ALPHA,
            1,                               # border-width
            PADDING * 2,                           # border-radius
            MID_GREEN_STRRGBA,        # border color
            PADDING,                                   # margin-bottom
            PADDING,                                   # margin-left
            PADDING,                                   # margin-right
            TOOLTIP
        )


    # GROUP_BOX_SS_TRANSPARENT
    GROUP_BOX_SS_TRANSPARENT = re.sub(
        background_color,
        'background-color: rgba(0,0,0,0',
        GROUP_BOX_SS
    )

    # GROUP_BOX_USER_NODE
    GROUP_BOX_USER_NODE = str(GROUP_BOX_SS)


    # GROUP_BOX_USER_SELECTED_NODE
    GROUP_BOX_USER_NODE_SELECTED = re.sub(
        background_color,
        'background-color: rgba(%s,%s' % (DARK_GREEN_STRI, ALPHA),
        GROUP_BOX_SS,
        1
    )
    GROUP_BOX_USER_NODE_SELECTED = re.sub(
        border_color,
        'border-color: rgba(%s' % (LOCAL_YELLOW_STRRGBA),
        GROUP_BOX_USER_NODE_SELECTED,
        1
    )

    # GROUP_BOX_EDIT_PARAMS
    GROUP_BOX_EDIT_PARAMS = re.sub(
        border_radius,
        'border-width: 2',
        GROUP_BOX_SS
    )
    GROUP_BOX_EDIT_PARAMS = re.sub(
        border_color,
        'border-color: rgba(%s' % (DARK_GREEN_STRRGBA),
        GROUP_BOX_EDIT_PARAMS
    )

    GROUP_BOX_HUDDISPLAY = \
        'QGroupBox::title{\
        subcontrol-origin: margin;\
        subcontrol-position: top center; \
        padding: -%spx %spx; \
        } \
        QGroupBox{\
            background-color: rgba(%s);\
            border-width: %spx; \
            border-radius: %spx;\
            border-style: solid; \
            border-color: rgba(%s); \
            margin-top: 1ex;\
        } \
        ' % (
            PADDING,
            PADDING * 2,
            FULL_TRANSPARENT_STRRGBA,
            1,                               # border-width
            PADDING * 2,                           # border-radius
            MID_GREEN_STRRGBA,        # border color
    )


#if __name__ == '__main__':
app = QApplication(sys.argv)
color_widget = ColorWidget()
color_widget.show()
sys.exit(app.exec_())
