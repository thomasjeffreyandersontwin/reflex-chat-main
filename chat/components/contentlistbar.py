import reflex as rx
from chat.state import State, Content

contentitem_style = dict(display="flex", flex_direction="column", width="80%", margin="auto")
message_style = dict(display="inline-block", padding="5px", border_radius="8px", max_width=["30em", "30em", "50em", "50em", "50em", "50em"])
input_style = dict(width="90%", height="80%", margin="5px auto")
expanded_style = dict(display="flex", flex_direction="row", align_items="center", justify_content="center")
innerbox_style = dict(border="1px solid white", border_radius="12px", margin="4px 0", width="100%")

class condCollapsedState(rx.State):
    f_collapsed: bool = True

    def on_collapse_expand(self):
        self.f_collapsed = not self.f_collapsed

def modal(trigger) -> rx.Component:
    """A modal to create a new document."""
    return rx.dialog.root(
        rx.dialog.trigger(trigger),
        rx.dialog.content(
            rx.hstack(  
                rx.input(
                    placeholder="Type something...",
                    on_blur=State.set_new_document_name,
                    width=["15em", "20em", "30em", "30em", "30em", "30em"],
                    background_color="white",
                    color="gray",
                    border=f"1px solid orange",
                    _placeholder={"color": "gray"},
                ),
                rx.dialog.close(
                    rx.button(
                        "Create document",
                        background_color=rx.color('orange', 9),
                        on_click=State.create_new_document,
                    ),
                ),
                # background_color=rx.color("orange", 12),
                spacing="2",
                width="100%",
            ),
            background_color="white",
            font_family="Switzer, sans-serif",
        ),
    )

def filectrl(url: str) -> rx.Component:
    """
    fileCtrl shows the vector file url
    """
    return rx.flex(
        rx.box(
            rx.upload(
                rx.button(
                    url,
                    padding="3px 10px",
                    border_radius="5px",
                    background_color=rx.color('orange', 9),
                    font_family="Switzer, sans-serif",
                ),
                padding='0',
                border="none",
                id="csv_upload",
                accept={
                    "Microsoft Word Files" :['.doc', '.docx'],
                    "CSV Files" :['.csv'],
                }
            ),
            rx.button(
                'Upload',
                on_click=State.handle_upload_csv(rx.upload_files(upload_id="csv_upload")),
                background_color=rx.color('orange', 9),
            ),
            width="100%",
            display="flex",
            justify_content="space-between",
            margin="10px",
        ),
        rx.box(
            rx.box(
                State.current_document,
                color=rx.color('orange', 9),
            ),
            documents_panel(),  
            modal(rx.button(
                "+ New Document", 
                background_color=rx.color('orange', 9),)),
            rx.button(
                rx.icon(
                    tag="trash",
                    on_click=State.delete_document,
                    stroke_width=1,
                ),
                width="14%",
                variant="soft",
                color_scheme="orange",
            ),
            width="100%",
            display="flex",
            justify_content="space-between",
            margin="10px",
        ),
        gap="5",
        justify='between',
        direction='column',
        padding="10px",
        width="100%",
    )

def document_item(document_name):
    return rx.menu.item(document_name, on_click=lambda:State.update_current_document(document_name))

def documents_panel() -> rx.Component:
    """A instruction bar with a collapsible/expandable button."""

    return rx.menu.root(
        rx.menu.trigger(
            rx.button("Documents",
                # on_click=State.retrieve_document_list(),
                background_color=rx.color('orange', 9),
            ),
        ),
        rx.menu.content(
            rx.foreach(State.document_list, document_item),
            background_color=rx.color('orange', 6),
            font_family="Switzer, sans-serif",
        ),
    )

def contentitem(con: Content) -> rx.Component:
    """
    contentitem can collapse/expand able
    contentitem contains 4 fields: title, text, token limit, vector entry
    display 3: title, text, token limit
    and edit 2: title, text
    """

    return rx.box(
        # flex box
        # conditional render
        rx.box(
            rx.cond(
                con.editing,
                rx.box(
                    # display expanded
                    # **expanded_style,
                    # title
                    rx.chakra.text_area(
                        value=con.edited_title,
                        on_change=lambda e:State.update_content_title(con, e),
                        background_color="white",
                        color="gray",
                        border=f"1px solid black",
                        **input_style,
                    ),

                    # text
                    rx.chakra.text_area(
                        value=con.edited_text,
                        on_change=lambda e:State.update_content_text(con, e),
                        background_color="white",
                        color="gray",
                        border=f"1px solid black",
                        **input_style,
                    ),

                    # save button
                    rx.box(
                        rx.button(
                            'Save',
                            background_color=rx.color('orange', 9),
                            on_click=State.handle_content_save(con),
                            margin="3px",
                        ),
                        rx.button(
                            'Cancel',
                            background_color=rx.color('orange', 9),
                            on_click=State.handle_entry_editing(con),
                            margin="3px",
                        ),
                        display="flex",
                        justify_content="center",
                        width="100%",
                    ),

                    # token
                    rx.box(
                        con.token,
                        **message_style,
                        font_style="italic",
                    ),

                    # vector entries
                    rx.box(
                        con.vector,
                        **message_style,
                        font_style="italic",
                    ),
                    background_color="white",
                    color="gray",
                    border=f"1px solid orange",
                    display="flex", 
                    align_items="flex-start",
                    flex_direction="column", 
                    width="100%", 
                ),
                rx.box(
                    # display collapsed
                    # **collapsed_style,
                    # title
                    rx.box(
                        con.title,
                        **message_style,
                        font_weight="bold",
                    ),

                    # text
                    rx.box(
                        con.text,
                        **message_style,
                        font_size="small",
                    ),

                    # token
                    rx.box(
                        'Token : ' + con.token,
                        **message_style,
                        font_style="italic",
                    ),

                    # vector
                    rx.box(
                        'Vector : ' + con.vector,
                        **message_style,
                        font_style="italic",
                    ),
                background_color="white",
                color="gray",
                border=f"1px solid orange",
                    display="flex", 
                    align_items="flex-start",
                    flex_direction="column", 
                    height=rx.cond(con.collapsed, "150px", "inherit"),
                    overflow=rx.cond(con.collapsed, "hidden", "visible"),
                ),
            ),
            **innerbox_style,
        ),
        # collapse button
        rx.box(
            rx.button(
                '+ -',
                on_click=State.handle_collapsed(con),
                height="40px",
                margin="3px",
                width="100%",
                background_color=rx.color('orange', 9),
            ),

            # edit button
            rx.button(
                'Edit',
                on_click=State.handle_entry_editing(con),
                height="40px",
                margin="3px",
                width="100%",
                background_color=rx.color('orange', 9),
            ),

            # edit button
            rx.button(
                'Delete',
                on_click=State.handle_entry_delete(con),
                height="40px",
                margin="3px",
                width="100%",
                background_color=rx.color('orange', 9),
            ),
            width="50px",
            display="flex",
            flex_direction="column",
        ),
        color="white",
        display="flex",
        flex_direction="row",
        align_items="flex-start",
        justify_content="space_between",
    )

def contentlistbar() -> rx.Component:
    """
    contentlistbar is shown right of the window
    each content can collapse/expand able
    each content has 4 fields and 3 fields are editable
    """

    return rx.vstack(
        filectrl(State.url),
        rx.box(rx.foreach(State.contents, contentitem)),
        overflow="auto",
        width="30%",
        height="100vh",
        padding="10px",
        border_left=f"1px solid {rx.color('orange', 9)}",
        background_color="white",
        font_family="Switzer, sans-serif",
    )