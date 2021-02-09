"""
TODO:
    * Figure out item height for defualts
    * selected item, pass to widget?  Doesn't work for click popup =\
            - passing previous value back? So clearing, and not setting?

"""

from qtpy.QtWidgets import QListView
from qtpy.QtCore import QModelIndex
from cgwidgets.settings.colors import iColor
from cgwidgets.settings.stylesheets import scroll_bar_ss


class CompleterPopup(QListView):
    def __init__(self, parent=None):
        super(CompleterPopup, self).__init__(parent)
        style_sheet_args = iColor.style_sheet_args
        style_sheet_args['scroll_bar'] = scroll_bar_ss
        style_sheet = """
        CompleterPopup{{
            border: 1px solid rgba{rgba_outline};
            background-color: rgba{rgba_gray_2};
            color: rgba{rgba_text};
        }}
        CompleterPopup::item:selected{{
            color: rgba{rgba_selected_hover};
            background-color: rgba{rgba_gray_4};
        }}
        CompleterPopup::item{{
            border: None ;
            background-color: rgba{rgba_gray_2};
            color: rgba{rgba_text};
        }}
        CompleterPopup::item:hover{{color: rgba{rgba_selected_hover}}}
        {scroll_bar}
        """.format(**style_sheet_args)

        self.setStyleSheet(style_sheet)

    def showEvent(self, event):
        if not self.model(): return
        row_count = self.model().rowCount(QModelIndex())

        if row_count == 0: return

        # how to get individual item height?
        #test = self.model().createIndex(0, 0, None)
        #print(self.visualRect(test))
        self.setMinimumHeight(100)

        return QListView.showEvent(self, event)
