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
        border: 2px dotted rgba{rgba_outline};
        /* background: rgba{rgba_outline}; */
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
        border: 2px dotted rgba{rgba_outline};
        /* background: rgba{rgba_outline}; */
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

# todo not in use...
# todo how to handle handle_length_margin arg?
# splitter_handle = """
# QSplitter::handle {{
#     border: 1px double rgba{rgba_handle};
#     margin: {handle_length_margin};
# }}
# QSplitter[is_handle_static=false]::handle:hover {{
#     border: 2px double rgba{rgba_handle_hover};
# }}
# QSplitter[is_handle_static=true]::handle {{
#     border: 1px solid rgba{rgba_handle};
#     margin: {handle_length_margin};
# }}
# """.format(**iColor.style_sheet_args)

# "type": type(self).__name__
"""
background: qradialgradient(
    radius: 0.9,
    cx:0.50, cy:0.50,
    fx:0.5, fy:0.5,
    stop:0.5 rgba{rgba_background},
    stop:0.75 rgba{rgba_selected});
}}

/*
{type}::hover{{
    background: qlineargradient(
        spread: repeat,
        x1:0.00, y1:0.00, x2:0.9, y2:0.9, x3:1, y3:1,
        stop:0 rgba{rgba_background},
        stop:0.5 rgba{rgba_selected_hover},
        stop:1 rgba{rgba_accept}
    );
}}
        
*/

"""