import os

import cgwidgets

class Icons(dict):
    def __init__(self):
        self._icons_dir = os.path.dirname(cgwidgets.__file__) + '/icons/'
        print(self._icons_dir)
        self['path_branch_open'] = self._icons_dir + 'branch_open.png'
        self['path_branch_closed'] = self._icons_dir + 'branch_closed.png'


icons = Icons()

