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
#from colors import iColor

def createRadialGradientSS(radius, center_radius, focal_radius, stops):
    """

    Args:
        radius:
        center_radius (tuple): center radius (float, float)
        focal_radius (tuple): focal radius (float, float)
        stops (list): [position (float), color_name (string)]
            ie  [0.5, "rgba_background"]

    """
    ss = """    
        background: qradialgradient(
        radius: {radius},
        cx:{cx}, cy:{cy},
        fx:{fx}, fy:{fy},
        """.format(
            radius=radius,
            cx=center_radius[0], cy=center_radius[1],
            fx=focal_radius[0], fy=focal_radius[1])

    stops_ss = ""
    for stop in stops:
        stops_ss += "stop:{pos} rgba{{{color_name}}},\n\t\t".format(pos=stop[0], color_name=stop[1])
    stops_ss = stops_ss

    # close CSS stylesheet
    ss += stops_ss[:-4] + ')'
    return ss

background_hover_radial = """
qradialgradient(
            radius: 0.9,
            cx:0.50, cy:0.50,
            fx:0.5, fy:0.5,
            stop:0.5 rgba{rgba_background},
            stop:0.75 rgba{rgba_selected_background});
"""
background_accept_radial = """
qradialgradient(
            radius: 0.9,
            cx:0.50, cy:0.50,
            fx:0.5, fy:0.5,
            stop:0.5 rgba{rgba_background},
            stop:0.75 rgba{rgba_accept});
"""
background_cancel_radial = """
qradialgradient(
            radius: 0.9,
            cx:0.50, cy:0.50,
            fx:0.5, fy:0.5,
            stop:0.5 rgba{rgba_background},
            stop:0.75 rgba{rgba_cancel});
"""
background_select_hover_radial = """
qradialgradient(
            radius: 0.9,
            cx:0.50, cy:0.50,
            fx:0.5, fy:0.5,
            stop:0.5 rgba{rgba_background},
            stop:0.75 rgba{rgba_selected_hover});
"""

input_widget_ss ="""
/* DEFAULT */
    {{type}}{{{{
        border: 1px dotted rgba{{rgba_gray_4}};
        border-radius: 10px;
        background-color: rgba{{rgba_background}};
        color: rgba{{rgba_text}};
        selection-background-color: rgba{{rgba_selected_background}};
    }}}}

    /* SELECTION */
    {{type}}[is_selected=true]{{{{
        background: {background_accept_radial}
        }}}}
    {{type}}[is_selected=false]{{{{
        background: {background_cancel_radial}
        }}}}
    {{type}}:focus{{{{
        background: {background_hover_radial}
        }}}}
    {{type}}::hover[hover_display=true]{{{{
        background: {background_select_hover_radial}
        }}}}
    {{type}}::hover:focus{{{{
            background: {background_hover_radial}
        }}}}
""".format(
    background_hover_radial=background_hover_radial,
    background_cancel_radial=background_cancel_radial,
    background_accept_radial=background_accept_radial,
    background_select_hover_radial=background_select_hover_radial)


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