import sys
import re
import json
import os

from PyQt5 import QtGui, QtCore, QtWidgets

# from Utils import Utils as Locals


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

    DARK_GREEN_RGB = QtGui.QColor()
    #DARK_GREEN_RGB.setRgbF(.016 * 255, .16827 * 255, .03560 * 255)
    DARK_GREEN_RGB.setRgb(18, 86, 36)

    DARK_GREEN_STRI = '16, 86, 36'
    DARK_GREEN_STRRGBA = '16, 86, 36, 255'
    #DARK_GREEN_STRI = '8, 86, 18'
    
    DARK_GREEN_HSV = QtGui.QColor()
    DARK_GREEN_HSV.setHsvF(.5, .9, .17)
    
    MID_GREEN_STRRGBA = '64, 128, 64, 255'
    
    
    LIGHT_GREEN_RGB = QtGui.QColor()
    #LIGHT_GREEN_RGB.setRgb(10.08525, 95.9463, 20.9814)
    LIGHT_GREEN_RGB.setRgb(90, 180, 90)
    LIGHT_GREEN_STRRGBA = '90, 180, 90, 255'
    
    DARK_RED_RGB = QtGui.QColor()
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
    
    #HOTKEYS = Locals().loadHotkeys()

    # ===============================================================================
    # HOTKEYS
    # ===============================================================================

'''
PREFERENCES_BUTTON_ICON = '/media/plt01/Downloads_web/dog-having-a-cupcake.jpg'
USER_HUD_ICON = '/home/brian/Pictures/pony.png'
HUD_LIST_ICON = '/home/brian/Pictures/lube.jpg'
LIGHT_LIST_ICON = '/home/brian/Pictures/mariolights.png'
GO_TO_NODE_ICON = '/home/brian/Pictures/arsemidget.jpg'

HOTKEYS = {
    'LIGHTS' : {'key' : 'A', 'icon' : LIGHT_LIST_ICON},
    'GOTONODE' : {'key' : 'S', 'icon' : GO_TO_NODE_ICON},
    'USERHUD' : {'key' : 'D', 'icon' : USER_HUD_ICON},
    'HUDLIST' : {'key' : 'F', 'icon':HUD_LIST_ICON},
    'PREFERENCES' : {'key' : 'G', 'icon' : PREFERENCES_BUTTON_ICON},
    'Center 0' : {'key' : '0', 'script' : '<path to file>', 'icon' : '<path to icon>'},
    'Center 1' : {'key' : '1', 'script' : '<path to file>', 'icon' : '<path to icon>'},
    'Center 2' : {'key' : '2', 'script' : '<path to file>', 'icon' : '<path to icon>'},
    'Center 3' : {'key' : '3', 'script' : '<path to file>', 'icon' : '<path to icon>'},
    'Center 4' : {'key' : '4', 'script' : '<path to file>', 'icon' : '<path to icon>'},
    'Center 5' : {'key' : '5', 'script' : '<path to file>', 'icon' : '<path to icon>'},
    'Center 6' : {'key' : '6', 'script' : '<path to file>', 'icon' : '<path to icon>'},
    'Center 7' : {'key' : '7', 'script' : '<path to file>', 'icon' : '<path to icon>'},
    'Center 8' : {'key' : '8', 'script' : '<path to file>', 'icon' : '<path to icon>'},
    'Center 9' : {'key' : '9', 'script' : '<path to file>', 'icon' : '<path to icon>'},
    }

file_name = '/media/ssd01/Katana/dev/resources/SuperTools/HUDCreate/Preferences/HOTKEYS.json'
if file_name:
    # Writing JSON data
    with open(file_name, 'w') as f:
        json.dump(HOTKEYS, f)
'''
'''
lo = 'border-style: solid; border-color: rgba(%s); margin-top: 1ex;'
#(\d+)x(\d+)
regex = r"border-color: .*?(?=\))"
pattern = re.search(regex, lo)
print(pattern)
replacedString = re.sub(regex, r'border-color: rgba(1,2,3,4)', lo)
print(lo)
print(replacedString)

#(.01600 .16827 .03560 | H128 S.9 V.17 L.12635

Lightest (stripes)
.03955 .37626 .08228 | H128 S.089 V.38 L.28351

Medium (fat stripes)
.03434 .33245 .07227 | H128 S.9 v.33 L.25034

app = QtWidgets.QApplication(sys.argv)
print(DARK_GREEN_RGB)
print(DARK_GREEN_HSV)
label = QtWidgets.QLabel()
label.setPixmap(DARK_GREEN_RGB)
label2 = QtWidgets.QLabel()
label2.setPixmap(DARK_GREEN_HSV)
sys.exit(app.exec_())

'''