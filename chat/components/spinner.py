import reflex as rx

from chat.components import loading_icon
from chat.state import QA, State
def spinner():
    return rx.flex(
        loading_icon(height="20%", fill="red"),
        width="100%",
        height="100%",
        justify="center",
        align="center",
        opacity="0.3",
        zIndex="1000",
        background_color="grey",
        position="absolute",
    )