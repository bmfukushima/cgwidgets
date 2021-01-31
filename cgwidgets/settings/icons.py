import os

import cgwidgets

class Icons(dict):
    def __init__(self):
        self._icons_dir = os.path.dirname(cgwidgets.__file__) + '/icons/'
        self['path_branch_open'] = self._icons_dir + 'branch_open.png'
        self['path_branch_closed'] = self._icons_dir + 'branch_closed.png'
        self['gradient_background'] = self._icons_dir + 'gradient_background.png'


icons = Icons()

