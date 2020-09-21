from collections import OrderedDict
import json
import os
import sys

from qtpy.QtWidgets import *

from .__utils__ import iUtils


class Settings(object):
    # PUBLISH WIDGET
    PUBLISH_CONTAINER_SS = iUtils.createGroupBoxSS(2, 5)
    PUBLISH_GROUP_CONTENT_MARGINS = 15

    # Views
    IMAGE_SELECTED_BORDER_WIDTH = 2
    IMAGE_SELECTED_SS = """
        border-width:{}px;\
        border-color: rgba(255,200,0,255);\
        border-style: solid\
    """.format(IMAGE_SELECTED_BORDER_WIDTH)
    IMAGE_DESELECTED_SS = iUtils.createThumbnailSS(IMAGE_SELECTED_BORDER_WIDTH, False)

    # IMAGE
    FULL_SCREEN_TEXT_SS = """
        background-color:rgba(64,64,64,128);
        color:rgb(200,200,32)
    """

    # TOP BAR
    TOP_BAR_CONTAINER_SS = iUtils.createGroupBoxSS(1, 20)
    # image sizes
    IMAGE_SIZES = OrderedDict()
    IMAGE_SIZES['small'] = 25
    IMAGE_SIZES['medium'] = 50
    IMAGE_SIZES['large'] = 100
    IMAGE_SIZES['xl'] = 300
    IMAGE_SIZES['american'] = 500

    # DEFAULTS
    DEFAULT_VIEW = 'Detailed'
    DEFAULT_SIZE = 'large'


if __name__ == '__main__':
    #s = Settings()
    IMAGE_SELECTED_BORDER_WIDTH = 2

    IMAGE_SIZES = OrderedDict()
    IMAGE_SIZES['small'] = 25
    IMAGE_SIZES['medium'] = 50
    IMAGE_SIZES['large'] = 100
    IMAGE_SIZES['xl'] = 300
    IMAGE_SIZES['american'] = 500
    print(IMAGE_SIZES)


    settings_dict = {
        # PUBLISH WIDGET
        'PUBLISH_CONTAINER_SS': iUtils.createGroupBoxSS(2, 5),
        'PUBLISH_GROUP_CONTENT_MARGINS': 15,
        # Views
        'IMAGE_SELECTED_BORDER_WIDTH': IMAGE_SELECTED_BORDER_WIDTH,
        'IMAGE_SELECTED_SS': [
            'border-width:{}px'.format(IMAGE_SELECTED_BORDER_WIDTH),
            'border-color: rgba(255,200,0,255)',
            'border-style: solid'
        ],
        'IMAGE_DESELECTED_SS': iUtils.createThumbnailSS(IMAGE_SELECTED_BORDER_WIDTH, False),
        # IMAGE
        'FULL_SCREEN_TEXT_SS': [
            'background-color:rgba(64,64,64,128)',
            'color:rgb(200,200,32)'
        ],

        # TOP BAR
        'TOP_BAR_CONTAINER_SS': iUtils.createGroupBoxSS(1, 20),
        # image sizes
        'IMAGE_SIZES': IMAGE_SIZES,

        # DEFAULTS
        'DEFAULT_SIZE': 'large',
    }
    
    settings_dir = os.environ['HOME'] + '/.library'
    settings_loc = settings_dir + '/settings.json'
    if not os.path.isdir(settings_dir):
        os.mkdir(settings_dir)

    if settings_loc:
        with open(settings_loc, 'w') as f:
            json.dump(settings_dict, f, indent=4, separators=(',', ':'))

    if settings_loc:
        with open(settings_loc, 'r') as f:
            datastore = json.load(f)
    
    app = QApplication(sys.argv)
    widget = QWidget()
    l = QVBoxLayout()
    t = QLabel('laksjdfkj')
    l.addWidget(t)
    widget.setLayout(l)
    widget.setStyleSheet(';'.join(datastore['FULL_SCREEN_TEXT_SS']))
    widget.show()
    
    sys.exit(app.exec_())

