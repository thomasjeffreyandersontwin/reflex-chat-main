import reflex as rx
from chat.state import State, Alert

def alertDialog() -> rx.Component:
    """An Alert

    Args:
        alert: Alert item.
    """
    return rx.flex(
        rx.box(
            rx.cond(
                State.alert.open,
                rx.flex(
                    rx.text(State.alert.title, font_size="large"),
                    rx.divider(),
                    rx.text(State.alert.message + State.alert.status),
                    rx.divider(),
                    rx.button("OK", on_click=State.hide_alert,
                        background_color=rx.color('orange', 6),),
                    background_color=rx.color('orange', 9),
                    justify="center",
                    align="center",
                    direction="column",
                    margin="10px",
                    width="30vw",
                    padding="12px",
                    border="1px solid grey",
                    border_radius="10px",
                ),
                rx.box(),
            ),
        ),
        width="100%",
        align="center",
        justify="center",
    )