"""
Note:
    When importing these into modules, if they don't have the string formatting, they will
    to have that the string formatting added later
        ie
    {splitter_handle_ss}
    .format(
        **style_sheet_args,
        splitter_handle_ss=splitter_handle_ss.format(**style_sheet_args)
    )
"""

from .colors import iColor

"""
Kwargs:
    rgba_invisible:
    rgba_outline
    
"""
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

input_widget_ss ="""
/* DEFAULT */
    {type}{{
        border: 1px dotted rgba{rgba_gray_4};
        border-radius: 10px;
        background-color: rgba{rgba_background};
        color: rgba{rgba_text};
        selection-background-color: rgba{rgba_selected_background};
    }}

    /* SELECTION */
    {type}[is_selected=true]{{
        background: qradialgradient(
            radius: 0.9,
            cx:0.50, cy:0.50,
            fx:0.5, fy:0.5,
            stop:0.5 rgba{rgba_background},
            stop:0.75 rgba{rgba_accept});
        }}
    {type}[is_selected=false]{{
        background: qradialgradient(
            radius: 0.9,
            cx:0.50, cy:0.50,
            fx:0.5, fy:0.5,
            stop:0.5 rgba{rgba_background},
            stop:0.75 rgba{rgba_cancel});
        }}
    {type}:focus{{
        background: qradialgradient(
            radius: 0.9,
            cx:0.50, cy:0.50,
            fx:0.5, fy:0.5,
            stop:0.5 rgba{rgba_background},
            stop:0.75 rgba{rgba_selected_background});
        }}
    {type}::hover[hover_display=true]{{
        background: qradialgradient(
            radius: 0.9,
            cx:0.50, cy:0.50,
            fx:0.5, fy:0.5,
            stop:0.5 rgba{rgba_background},
            stop:0.75 rgba{rgba_selected_hover});
        }}
    {type}::hover:focus{{
        background: qradialgradient(
            radius: 0.9,
            cx:0.50, cy:0.50,
            fx:0.5, fy:0.5,
            stop:0.5 rgba{rgba_background},
            stop:0.75 rgba{rgba_selected_background});
        }}

"""

"""
Kwargs:
    handle_length_margin: <int>px <int>px
    rgba_handle_hover: (r, g, b, a)
    rgba_handle: (r, g, b, a)
Properties:
    is_handle_visible
    is_handle_static
"""
splitter_handle_ss = """
/* HANDLE ;*/
    {type}[is_handle_visible=true]::handle {{
        border: 2px dotted rgba{rgba_handle};
        margin: {handle_length_margin};
    }}
    
    /* VISIBLE */
    {type}[is_handle_visible=false]::handle {{
        border: None;
        margin: 0px;
    }}

    /* STATIC HANDLE */
    {type}[is_handle_visible=true][is_handle_static=false]::handle:hover {{
        border: 2px dotted rgba{rgba_handle_hover};
    }}

    {type}[is_handle_visible=true][is_handle_static=true]::handle {{
        border: 2px dotted rgba{rgba_handle};
    }}
"""


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