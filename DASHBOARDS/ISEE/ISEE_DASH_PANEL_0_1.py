import panel as pn
import numpy as np
from matplotlib.figure import Figure

#pn.extension(sizing_mode="stretch_width", template="")
pn.extension(template='fast')

bins=pn.widgets.IntSlider(value=20, start=10, end=30, step=1, name="Slider")

#===============================================================================
# row1=pn.Row(
#     bins,
#     pn.pane.Image(
#         "https://panel.holoviz.org/_images/logo_horizontal_light_theme.png",
#         align="center",
#     ),)
#===============================================================================

#bins = pn.widgets.IntSlider(value=20, start=10, end=30, step=1, name="Bins")
#pn.Column(row1, pn.pane.Str(bins)).servable()

def text(bins):
    return f'{bins} is a text'

pn.Column(
    bins,
    pn.pane.Markdown(pn.bind(text, bins))).servable(target='sidebar')
    
pn.Column(pn.pane.Image(
        "https://panel.holoviz.org/_images/logo_horizontal_light_theme.png",
        align="center",
    )).servable(target='main')
    
    
    