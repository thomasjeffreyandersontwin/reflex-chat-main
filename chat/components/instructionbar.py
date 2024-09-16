import reflex as rx
from chat.state import State

collapsebut_style = dict(width="6px", height="100%", margin="auto", padding="0")
textinstrut_style = dict(width="96%", height="80%", margin="13px" )
save_button_style = dict(width="40%", height="30px", margin="auto")
instrut_bar_style = dict(display="flex", justifyContent="space-between", height="100%")
flex_box_style =    dict(display="flex", flexDirection="column", width="100%", height="100%", justifyContent="center", alignItems="center")


def collpase_expand_button() -> rx.Component:
    """collpase_expand_button handles a long collapse/expand button."""
    return rx.button(
        "•",
        **collapsebut_style,
        background_color=rx.color('orange', 9),
    )

def instruction_pane() -> rx.Component:
    """A instruction bar with a collapsible/expandable button."""

    return rx.box(
        rx.box(
            rx.text_area(
                value=State.instruction,
                on_change=State.set_instruction,
                background_color="white",
                color="gray",
                border=f"1px solid orange",
                **textinstrut_style
            ),
            rx.flex(
                rx.button(
                    'Save',
                    **save_button_style,
                    background_color=rx.color('orange', 9),
                    on_click=State.handle_instruction_update(),
                ),
                rx.button(
                    'Load',
                    **save_button_style,
                    on_click=lambda:State.handle_load_instruction(),
                    background_color=rx.color('orange', 9),
                ),
                justify='center',
            ),
            **flex_box_style,
        ),
        **instrut_bar_style,
    )

def model_pane() -> rx.Component:
    """A instruction bar with a collapsible/expandable button."""

    return rx.menu.root(
        rx.menu.trigger(
            rx.button("Models",
                background_color=rx.color('orange', 9),
            ),
        ),
        rx.menu.content(
            rx.menu.item("GPT 4.0", shortcut="⌘ E", on_click=lambda:State.update_model('gpt-4-turbo')),
            rx.menu.item("3.5 turbo", shortcut="⌘ D", on_click=lambda:State.update_model('gpt-3.5-turbo')),
            rx.menu.separator(),
            rx.menu.item("Fine Tuned Model1", shortcut="⌘ N"),
            rx.menu.item("Fine Tuned Model2", shortcut="⌘ M"),
            rx.menu.separator(),
            rx.menu.sub(
                rx.menu.sub_trigger("etc"),
                rx.menu.sub_content(
                    rx.menu.item("Fine Tuned Model2", shortcut="⌘ M"),
                ),
            ),
            background_color=rx.color('orange', 6),
            font_family="Switzer, sans-serif",
    ),
)


def sidebar(trigger) -> rx.Component:
    """The sidebar component."""
    return rx.drawer.root(
        rx.drawer.trigger(trigger),
        rx.drawer.overlay(),
        rx.drawer.portal(
            rx.drawer.content(
                rx.vstack(
                    rx.heading("Instruction", color=rx.color("orange", 11), font_family="Switzer, sans-serif",),
                    rx.divider(),
                    instruction_pane(),
                    model_pane(),
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


def instructionbar():
    return rx.box(
        sidebar(
            collpase_expand_button(),
        ),
        backdrop_filter="auto",
        backdrop_blur="lg",
        padding="1px",
        # border_bottom=f"1px solid {rx.color('orange', 3)}",
        background_color="white",
        display="flex",
        position="sticky",
        top="0",
        z_index="100",
        align_items="center",
        height="100vh",
    )
