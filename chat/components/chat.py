import reflex as rx

from chat.components import loading_icon
from chat.state import QA, State


message_style = dict(display="inline-block", padding="1em", border_radius="8px", max_width=["30em", "30em", "50em", "50em", "50em", "50em"])
ragctrl_style = dict(display="flex", justifyContent="space-around", margin="10px", gap="5px", width="300px")
insctrl_style = dict(display="flex", justifyContent="space-around", margin="10px", gap="5px", width="300px")

input_style = {
    'border': '1px solid black',
    'background-color': 'white',
    'color': 'black',
    '::placeholder':{
        'color':'#ff0000',
    },
}

class messageState(rx.State):
    question: str
    answer: str

    async def handle_edit_QA(self, qa: QA):
        org_qa = QA(question=qa['question'], answer=qa['answer'], editing=False)
        self.question = org_qa.question
        self.answer = org_qa.answer
        print('handle edit QA : ', qa)
        State.handle_edit_QA(qa)

def message(qa: QA) -> rx.Component:
    """A single question/answer message.

    Args:
        qa: The question/answer pair.

    Returns:
        A component displaying the question/answer pair.
    """
    return rx.cond(
        qa.editing,
        rx.box(
            rx.flex(
                rx.flex(
                    rx.button(
                        'Save',
                        background_color=rx.color('orange', 9),
                        on_click=lambda:State.handle_save_QA(qa),
                    ),
                    rx.button(
                        'Cancel',
                        background_color=rx.color('orange', 9),
                        on_click=lambda:State.handle_canceledit_QA(qa),
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.box(
                    rx.chakra.text_area(
                        value=State.question,
                        background_color="white",
                        color="gray",
                        border=f"1px solid orange",
                        on_change=State.set_question,
                    ),
                    text_align="right",
                    margin_top="1em",
                ),
                spacing="2",
                justify="between",
                align="center",
            ),
            rx.box(
                rx.chakra.text_area(
                    value=State.answer,
                    background_color="white",
                    color="gray",
                    border=f"1px solid orange",
                    on_change=State.set_answer,
                    height="0px",
                ),
                text_align="left",
                padding_top="1em",
            ),
            width="100%",
        ),
        rx.box(
            rx.flex(
                rx.flex(
                    rx.button(
                        'Edit',
                        background_color=rx.color('orange', 9),
                        on_click=lambda:State.handle_edit_QA(qa),
                    ),
                    rx.button(
                        'Delete',
                        background_color=rx.color('orange', 9),
                        on_click=lambda:State.handle_remove_QA(qa),
                    ),
                    spacing='1',
                ),
                rx.box(
                    rx.markdown(
                        qa.question,
                        background_color="white",
                        color="gray",
                        border=f"1px solid orange",
                        **message_style,
                    ),
                    text_align="right",
                    margin_top="1em",
                ),
                spacing="2",
                justify="between",
                align="center",
            ),
            rx.box(
                rx.markdown(
                    qa.answer,
                    background_color="white",
                    color="gray",
                    border=f"1px solid orange",
                    **message_style,
                ),
                text_align="left",
                padding_top="1em",
            ),
            width="100%",
        ),
    )

from chat.components.alert import alertDialog

def chat() -> rx.Component:
    """List all the messages in a single conversation."""
    return rx.vstack(
        alertDialog(),
        rx.box(
            rx.box(
                rx.box(rx.foreach(State.chats[State.current_chat], message), width="100%"),
                py="8",
                flex="1",
                width="100%",
                max_width="50em",
                padding_x="4px",
                align_self="center",
                overflow="hidden",
                padding_bottom="5em",
                margin="auto",
            ),
            width="100%",
            height="100%",

        ),
        width="100%",
        height="calc(100vh - 220px)",
        overflow="auto",
    )

def instruction_ctrl():
    """The instruction_ctrl handles Instruction Input"""
    return rx.box(
        rx.input(
            type='number',
            value=State.rag_limit,
            on_change=State.set_rag_limit,
            background_color="white",
            color="black",
            border=f"1px solid orange",
        ),
        rx.button(
            'Submit Rag Limit',
            background_color=rx.color('orange', 9),
        ),
        **insctrl_style,
    )

def ragInput_ctrl():
    """The ragInput_ctrl handles Rag Limit & Rag Response"""
    return rx.box(
        rx.box(
            rx.input(
                type='number',
                value=State.rag_limit,
                on_change=State.set_rag_limit,
                background_color="white",
                color="black",
                border=f"1px solid orange",
            ),
            rx.button(
                'Submit Rag Limit',
                background_color=rx.color('orange', 9),
                on_click=lambda:State.handle_raglimit_update(),
            ),
            **ragctrl_style,
        ),
        rx.box(
            rx.input(
                type='number',
                value=State.rag_response,
                on_change=State.set_rag_response,
                background_color="white",
                color="black",
                border=f"1px solid orange",
            ),
            rx.button(
                'Submit Rag Response',
                background_color=rx.color('orange', 9),
                on_click=lambda:State.handle_ragresponse_update(),
            ),
            **ragctrl_style,
        ),
    )

collapsebut_style = dict(width="6px", height="100%", padding="0")
textinstrut_style = dict(width="80%", height="80%", margin="13px" )
save_button_style = dict(width="40%", height="30px", margin="auto")
instrut_bar_style = dict(display="flex", position="absolute", width="300px", height="100vh", justifyContent="space-between")
flex_box_style =    dict(display="flex", flexDirection="column", width="100%", height="100%", justifyContent="center", alignItems="center")

def instructionbar() -> rx.Component:
    """A instruction bar with a collapsible/expandable button."""
    def collpase_expand_button() -> rx.Component:
        """collpase_expand_button handles a long collapse/expand button."""
        return rx.button(
            "•",
            background_color=rx.color('orange', 9),
            **collapsebut_style,
        )

    return rx.box(
        rx.box(
            rx.text_area(
                **textinstrut_style
            ),
            rx.button(
                'Save',
                on_click=lambda:State.handle_instruction_update(),
                background_color=rx.color('orange', 9),
                border_radius="15px",
                **save_button_style
            ),
            **flex_box_style,
        ),
        collpase_expand_button(),
        background_color=rx.color('white'),
        **instrut_bar_style,
    )

def action_bar() -> rx.Component:
    """The action bar to send a new message."""
    return rx.box(
        ragInput_ctrl(),
        rx.center(
            rx.vstack(
                rx.chakra.form(
                    rx.chakra.form_control(
                        rx.hstack(
                            rx.radix.text_field.root(
                                rx.radix.text_field.input(
                                    placeholder="Type something...",
                                    id="question",
                                    width=["15em", "20em", "45em", "50em", "50em", "50em"],
                                    color="black",
                                    background_color="white",
                                    border="1px solid black",
                                    style=input_style,
                                ),
                                rx.radix.text_field.slot(
                                    rx.tooltip(
                                        rx.icon("info", size=18),
                                        content="Enter a question to get a response.",
                                    )
                                ),
                            ),
                            rx.button(
                                rx.cond(
                                    State.processing,
                                    loading_icon(height="1em"),
                                    rx.text("Send"),
                                ),
                                background_color=rx.color('orange', 9),
                                type="submit",
                            ),
                            align_items="center",
                        ),
                        is_disabled=State.processing,
                    ),
                    on_submit=State.process_question,
                    reset_on_submit=True,
                ),
                rx.text(
                    "Agile by Design Chat may provide excllent answers to Jeff Anderson.",
                    text_align="center",
                    font_size=".75em",
                    color=rx.color("orange", 10),
                ),
                # rx.logo(margin_top="-1em", margin_bottom="-1em"),
                align_items="center",
            ),
        ),
        display="flex",
        position="sticky",
        bottom="0",
        left="0",
        padding_y="16px",
        backdrop_filter="auto",
        backdrop_blur="lg",
        border_top=f"1px solid {rx.color('orange', 9)}",
        background_color="white",
        align_items="stretch",
        width="100%",
        height="160px",
    )
