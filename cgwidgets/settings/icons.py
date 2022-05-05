import os

import cgwidgets

class Icons(dict):
    def __init__(self):
        self._icons_dir = (os.path.dirname(__file__) + '/icons/').replace("\\", "/")
        self['path_branch_open'] = self._icons_dir + 'branch_open.png'
        self['path_branch_closed'] = self._icons_dir + 'branch_closed.png'
        self['gradient_background'] = self._icons_dir + 'gradient_background.png'
        self['example_image_01'] = self._icons_dir + 'example_image_01.png'
        self['example_image_02'] = self._icons_dir + 'example_image_02.png'
        self["ACCEPT_GIF"] = self._icons_dir + '/accept.gif'
        self["CANCEL_GIF"] = self._icons_dir + '/cancel.gif'
        self["update"] = self._icons_dir + "/recycle.png"

icons = Icons()

