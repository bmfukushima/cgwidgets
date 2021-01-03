from .colors import iColor

scroll_bar_ss = """
/* HORIZONTAL */
    /* BACKGROUND */
    QScrollBar:horizontal {{
        border: None;
        background: rgba{rgba_invisible};
        height: 5px;
        margin: 0px 0px 0px 0px;
    }}
    
    /* MOVING PART */
    QScrollBar::handle:horizontal {{
        background: rgba{rgba_blue_3};
        width: 10px;
    }}
    
    /* MODIFY BUTTONS AT ENDS */
    QScrollBar::add-line:horizontal {{
        border: None;
        background: None;
        width: 0px;
        subcontrol-position: right;
        subcontrol-origin: margin;
    }}
    QScrollBar::sub-line {{
        border: None;
        background: None;
        width: 0px;
        subcontrol-position: left;
        subcontrol-origin: margin;
    }}

/* VERTICAL */
/* BACKGROUND */
    QScrollBar:vertical {{
        border: None;
        background: rgba{rgba_invisible};
        width: 5px;
        margin: 0px 0px 0px 0px;
    }}
    
    /* MOVING PART */
    QScrollBar::handle:vertical {{
        background: rgba{rgba_blue_3};
        height: 10px;
    }}
    
    /* MODIFY BUTTONS AT ENDS */
    QScrollBar::add-line:vertical {{
        border: None;
        background: None;
        height: 0px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }}
    QScrollBar::sub-line {{
        border: None;
        background: None;
        height: 0px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }}
""".format(**iColor.style_sheet_args)
