import reflex as rx
from chat.state import State

def sidebar_chat(chat: str) -> rx.Component:
    """A sidebar chat item.

    Args:
        chat: The chat item.
    """
    return  rx.drawer.close(rx.hstack(
        rx.button(
            chat, on_click=lambda: State.set_chat(chat), width="72%", variant="surface",
            background_color=rx.color('orange', 9),
            color="white",
        ),
        rx.button(
            rx.icon(
                tag="trash",
                on_click=State.delete_chat,
                stroke_width=1,
            ),
            width="14%",
            variant="soft",
            color_scheme="orange",
        ),
        rx.button(
            rx.chakra.icon(
                tag="email",
                on_click=State.submit_chat,
                stroke_width=1,
            ),
            width="14%",
            variant="soft",
            color_scheme="orange",
        ),
        width="100%",
    ))


def sidebar(trigger) -> rx.Component:
    """The sidebar component."""
    return rx.drawer.root(
        rx.drawer.trigger(trigger),
        rx.drawer.overlay(),
        rx.drawer.portal(
            rx.drawer.content(
                rx.vstack(
                    rx.heading("Chats", color=rx.color("orange", 11), font_family="Switzer, sans-serif",),
                    rx.divider(),
                    rx.foreach(State.chat_titles, lambda chat: sidebar_chat(chat)),
                    align_items="stretch",
                    width="100%",
                ),
                top="auto",
                right="auto",
                height="100%",
                width="20em",
                padding="2em",
                background_color="white",
                outline="none",
                font_family="Switzer, sans-serif",
            )
        ),
        direction="left",
    )


def modal(trigger) -> rx.Component:
    """A modal to create a new chat."""
    return rx.dialog.root(
        rx.dialog.trigger(trigger),
        rx.dialog.content(
            rx.hstack(
                rx.input(
                    placeholder="Type something...",
                    on_blur=State.set_new_chat_name,
                    width=["15em", "20em", "30em", "30em", "30em", "30em"],
                    background_color="white",
                    color="black",
                    border=f"1px solid orange",
                    _placeholder={"color": "gray"},
                ),
                rx.dialog.close(
                    rx.button(
                        "Create chat",
                        on_click=State.create_chat,
                        background_color=rx.color('orange', 9),
                    ),
                ),
                # background_color=rx.color("orange", 12),
                spacing="2",
                width="100%",
                font_family="Switzer, sans-serif",
            ),
            background_color="white",
        ),
    )


def navbar():
    return rx.box(
        rx.hstack(
            rx.hstack(
                # rx.avatar(fallback="RC", variant="solid", background_color=rx.color('orange', 9),),
                rx.image(src="logo.svg", width="100px", height="auto"),
                rx.heading("Agile by Design Chat", font_family="Switzer, sans-serif",),
                rx.desktop_only(
                    rx.badge(
                    State.current_chat,
                    rx.tooltip(rx.icon("info", size=14), content="The current selected chat."),
                    variant="soft",
                    background_color=rx.color('orange', 8, 5),
                    color="white",
                    )
                ),
                color=rx.color('orange', 9),
                align_items="center",
                font_family="Switzer, sans-serif",
            ),
            rx.hstack(
                modal(rx.button("+ New chat",
                    background_color=rx.color('orange', 9),
                )),
                sidebar(
                    rx.button(
                        rx.icon(
                            tag="messages-square",
                            color=rx.color("orange", 12),
                        ),
                        background_color=rx.color("orange", 9),
                    )
                ),
                rx.desktop_only(
                    rx.button(
                        rx.icon(
                            tag="sliders-horizontal",
                            color=rx.color("orange", 12),
                        ),
                        background_color=rx.color("orange", 6),
                    )
                ),
                rx.button("Load All Data",
                    background_color=rx.color('red', 9),
                    on_click=State.load_all_data
                ),
                align_items="center",
            ),
            justify_content="space-between",
            align_items="center",
        ),
        backdrop_filter="auto",
        backdrop_blur="lg",
        padding="12px",
        border_bottom=f"1px solid {rx.color('orange', 9)}",
        background_color="white",
        position="sticky",
        top="0",
        z_index="100",
        align_items="center",
        justify_content="center",
        height="60px",
    )
