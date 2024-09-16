"""The main Chat app."""

import reflex as rx
from chat.components import chat, navbar
from chat.components.instructionbar import instructionbar
from chat.components.contentlistbar import contentlistbar
from chat.components.spinner import spinner
from chat.state import State

flexcontainer_style = dict(display="flex", justify_content="center")

def index() -> rx.Component:
    """The main app."""
    return rx.box(
        rx.cond(
            State.spinner_show,
            spinner(),
        ),
        instructionbar(),
        rx.chakra.vstack(
            navbar(),
            chat.chat(),
            chat.action_bar(),
            background_color="white",
            color=rx.color("orange", 12),
            min_height="100vh",
            width="100%",
            align_items="stretch",
            spacing="0",
            font_family="Switzer, sans-serif",
        ),
        contentlistbar(),
        font_family="Switzer, sans-serif",
        **flexcontainer_style
    )


style = {
    'font_family': "Switzer, sans-serif",
    'button': {
        'font_weight': 'bold',
    },
    '::placeholder': {
        'color': "gray"
    },
    '.menu_item' : {
        '::hover':{
            'color':'red',
        },
        '::active':{
            'color':'blue',
        },
    },
}
# Add state and page to the app.
app = rx.App(   
    theme=rx.theme(
        appearance="dark",
        accent_color="violet",
    ),
    style=style,
)
app.add_page(index)
