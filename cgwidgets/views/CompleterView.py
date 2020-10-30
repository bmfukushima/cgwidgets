from qtpy.QtWidgets import QListView
from cgwidgets.settings.colors import iColor


class CompleterPopup(QListView):
    def __init__(self, parent=None):
        super(CompleterPopup, self).__init__(parent)
        style_sheet_args = iColor.style_sheet_args

        style_sheet = """
        CompleterPopup{{
            border: 1px solid rgba{rgba_outline};
            background-color: rgba{rgba_gray_0};
            color: rgba{rgba_text};
        }}
        CompleterPopup::item:selected{{
            color: rgba{rgba_hover};
            background-color: rgba{rgba_gray_2};
        }}
        CompleterPopup::item:hover{{color: rgba{rgba_hover}}}
        CompleterPopup::item{{
            border: None ;
            background-color: rgba{rgba_gray_0};
            color: rgba{rgba_text};
        }}

        """.format(**style_sheet_args)

        self.setStyleSheet(style_sheet)
