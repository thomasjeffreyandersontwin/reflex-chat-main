import os
import reflex as rx
from openai import OpenAI
from gpt.document import *
from gpt.GPT_API_Facade import * 

# Checking if the API key is set properly
#if not os.getenv("OPENAI_API_KEY"):
#    raise Exception("Please set OPENAI_API_KEY environment variable.")


class QA(rx.Base):
    """A question and answer pair."""

    question: str
    answer: str
    editing: bool # represents if question-answer is being editend in the chat panel


class Content(rx.Base):
    """A question and answer pair."""

    title: str
    edited_title: str
    text: str
    edited_text: str
    token: str
    vector: str
    collapsed: bool
    editing: bool


class Alert(rx.Base):
    """Alert with status."""

    title: str
    status: str
    message: str
    open: bool

DEFAULT_CHATS = {
    "Intros": [],
}

DEFAULT_COLORS = {
    'primary': 'orange',
    'secondary': 'white',
}


DEFAULT_CONTENTS = []

class State(rx.State):
    """The app state."""

    # Mockup Contents list from vecor entries file
    contents: list[Content] = DEFAULT_CONTENTS 

    # A dict from the chat name to the list of questions and answers.
    chats: dict[str, list[QA]] = DEFAULT_CHATS

    # The current chat name.
    current_chat = "Intros"

    # The current question.
    question: str

    # The current alert states.
    alert: Alert = Alert(title="", status="", message="", open=False)

    # The current answer.
    answer: str

    # The instruction
    instruction: str

    # The instruction
    model: str = "gpt-4-turbo"

    # The instruction
    url: str = 'Click here to upload a csv'

    # Whether we are processing the question.
    processing: bool = False

    # The name of the new chat.
    new_chat_name: str = ""

    # The name of the new chat.
    new_document_name: str = ""
  
    # The limit of similar contents count.
    rag_limit: int = 4000
  
    # The limit that is used for chat gpt answer.
    rag_response: int = 40000

    # Flag representing if alert is shown.
    flag_shown_alert: bool = False

    # The name of the content document.
    current_document: str = ""
    document_list: list[str] = []

    spinner_show = False

    # ------------------------General------------------------

    def show_spin(self):
        self.spinner_show = True

    def hide_spin(self):
        self.spinner_show = False

    def get_facade(self):
        if self.document_list == []:
            self.retrieve_document_list()
        return GPTAPIFacade.GetInstance(self.current_document)

    async def load_all_data(self):
        self.show_spin()

        facade = self.get_facade()
        self.instruction = facade.load_instruction_from_file()
        self.load_chat()
  
        self.hide_spin()

    # //////////////////////////General//////////////////////////

    # ------------------------About Chat History------------------------
    def create_chat(self):
        """Create a new chat."""
        # Add the new chat to the list of chats.
        self.current_chat = self.new_chat_name
        self.chats[self.new_chat_name] = []

    def delete_chat(self):
        """Delete the current chat."""
        del self.chats[self.current_chat]
        if len(self.chats) == 0:
            self.chats = DEFAULT_CHATS
        self.current_chat = list(self.chats.keys())[0]

    async def submit_chat(self):
        """Submit the current chat."""
        self.show_spin()

        # Refactor to handle embedding heading
        facade = await GPTAPIFacade.createNewChatCSV(self.current_chat)
        headings = []
        for chat in self.chats[self.current_chat]:
            heading = Heading(title=chat.question) # for embedding.
            heading.text = chat.answer
            headings.append(heading)

        headingswithEmbedding = facade.calculate_embeddings_for_headings(headings) # refactored existing calculate_embeddings with man-made heading.

        # document_source = facade.document_source.data_documents[0]
        document_source = facade.document_source
        for heading in headingswithEmbedding:
            document_source.headings.append(heading)
        document_source.save_to_csv(subFolder='chats')
        self.show_chat_embed_alert('success')

        self.hide_spin()

    def load_chat(self):
        """Load all the chat history."""

        # Refactor to handle embedding heading
        facade = GPTAPIFacade.GetChatsInstance()
        document_source = facade.document_source
        for document in document_source.data_documents:
            # print(document.filepath)
            document.load_from_csv(subFolder='chats')
            chat_name = document.filepath
            self.current_chat = chat_name
            self.new_chat_name = chat_name
            self.create_chat()

            for heading in document.headings:
                qa = QA(question=heading.title, answer=heading.text , editing=False)
                self.chats[self.current_chat].append(qa)
                self.question = qa.question
                self.answer = qa.answer
                facade.track_conversation(self.question, self.answer)

    def set_chat(self, chat_name: str):
        """Set the name of the current chat.

        Args:
            chat_name: The name of the chat.
        """
        self.current_chat = chat_name

    @rx.var
    def chat_titles(self) -> list[str]:
        """Get the list of chat titles.

        Returns:
            The list of chat names.
        """
        return list(self.chats.keys())

    # ///////////////////////About Chat History///////////////////////

    async def process_question(self, form_data: dict[str, str]):
        # Get the question from the form
        question = form_data["question"]

        # Check if the question is empty
        if question == "":
            return

        model = self.openai_process_question

        async for value in model(question):
            yield value
    
    def other_method(self):
        print("other method is called")


    # ------------------------About Question and Answer------------------------
    async def openai_process_question(self, question: str):
        self.show_spin()

        facade = self.get_facade()


        # Add the question to the list of questions.
        qa = QA(question=question, answer="" , editing=False)
        self.chats[self.current_chat].append(qa)

        # Clear the input and the processing.
        self.processing = True
        yield

        # Build the messages.
        messages = [
            {
                "role": "system",
                "content": "You are a friendly chatbot named Reflex. Respond in markdown.",
            }
        ]
        
        messages = facade.prep_gpt_4_answer(question)
        for qa in self.chats[self.current_chat]:
            messages.append({"role": "user", "content": qa.question})
            messages.append({"role": "assistant", "content": qa.answer})

        # Remove the last mock answer.
        messages = messages[:-1]

        response = facade.answer_with_gpt_4(question) # receive streaming data
        response_content = ""
        for item in response:
            if hasattr(item.choices[0].delta, "content"):
                answer_text = item.choices[0].delta.content
                # Ensure answer_text is not None before concatenation
                if answer_text is not None:
                    self.chats[self.current_chat][-1].answer += answer_text
                    response_content += answer_text
                else:
                    # Handle the case where answer_text is None, perhaps log it or assign a default value
                    # For example, assigning an empty string if answer_text is None
                    answer_text = ""
                    self.chats[self.current_chat][-1].answer += answer_text
                    response_content += answer_text
                self.chats = self.chats
                yield

        facade.track_conversation(question, response_content)

        self.question = question

        self.other_method()
        self.update_content_list(facade)

        # Toggle the processing flag.
        self.processing = False
        
        self.hide_spin()

    def handle_save_QA(self, qa : QA):
        self.show_spin()

        f_qa = QA(question=qa['question'], answer=qa['answer'], editing=True)
        try:
            idx = self.chats[self.current_chat].index(f_qa)
            if idx > -1:
                org_qa = self.chats[self.current_chat][idx]
                org_qa.answer = self.answer
                org_qa.question = self.question
                org_qa.editing = False
                self.chats[self.current_chat][idx] = org_qa
                print("QA Changed To: ", org_qa)


                # Refactor to handle embedding heading
                facade = self.get_facade()
                heading = Heading(title=self.question) # for embedding.
                heading.text = self.answer
                # refactored existing calculate_embeddings with man-made heading.
                headingwithEmbedding = facade.calculate_embeddings_for_heading(heading) 
                try:
                    document_source = facade.document_source
                    document_source.headings.append(headingwithEmbedding)
                    document_source.save_to_csv()
                    document_source.load_from_csv()
                    self.show_QA_embed_alert('success')
                except KeyError:
                    print("error : no documents")

        except Exception as e:
            print(f"Error occured : {e}")

        self.hide_spin()

    def show_QA_embed_alert(self, status='success'):
        self.alert.open = True
        self.alert.message = 'Current QA '
        self.alert.title = 'Embedding a question & answer'
        if status == 'success':
            self.alert.message = self.alert.message + ' successfully embedded'
        elif status == 'failed':
            self.alert.message = self.alert.message + ' embedding failed'

    def handle_canceledit_QA(self, qa : QA):
        f_qa = QA(question=qa['question'], answer=qa['answer'], editing=True)
        try:
            idx = self.chats[self.current_chat].index(f_qa)
            if idx > -1:
                org_qa = self.chats[self.current_chat][idx]
                org_qa.editing = False
                self.chats[self.current_chat][idx] = org_qa
                print("QA Changed To: ", org_qa)
        except Exception as e:
            print(f"Error occured : {e}")

    async def handle_edit_QA(self, qa: QA):
        print('editing : ', qa)
        f_qa = QA(question=qa['question'], answer=qa['answer'], editing=False)
        try:
            idx = self.chats[self.current_chat].index(f_qa)
            if idx > -1:
                org_qa = self.chats[self.current_chat][idx]
                self.question = org_qa.question
                self.answer = org_qa.answer
                org_qa.editing = True
                self.chats[self.current_chat][idx] = org_qa
                print("QA Changed To: ", org_qa)
        except Exception as e:
            print(f"Error occured : {e}")

    async def handle_remove_QA(self, qa: QA):
        f_qa = QA(question=qa['question'], answer=qa['answer'], editing=False)
        try:
            self.chats[self.current_chat].remove(f_qa)
        except Exception as e:
            print(f"Error occured : {e}")

    # ////////////////////////////About Question and Answer////////////////////////////

    def update_model(self, model: str):
        self.model = model
        facade = self.get_facade()
        facade.update_model(self.model)
        # continue to facade


    def show_chat_embed_alert(self, status='success'):
        self.alert.open = True
        self.alert.message = 'Current chat '
        self.alert.title = 'Embedding entire chat'
        if status == 'success':
            self.alert.message = self.alert.message + ' successfully embedded'
        elif status == 'failed':
            self.alert.message = self.alert.message + ' embedding failed'

    def hide_alert(self):   
        self.alert.open = False
            
    # ------------------------About Entry------------------------
    
    def retrieve_document_list(self):
        self.document_list = GPTAPIFacade.retrieve_document_list()
        self.current_document = self.document_list[0]
        print("retrieve called", self.current_document)
    
    async def create_new_document(self):
        # code to create new document in facade
        if self.document_list == []:
            self.retrieve_document_list()
        facade = await GPTAPIFacade.createNewDocument(self.new_document_name)


        #for front end
        self.document_list.append(self.new_document_name)
        # self.update_current_document(self.new_document_name, facade)
        self.current_document = self.new_document_name
        self.new_document_name = ""
        pass

    def delete_document(self):
        if self.current_document != "":
            self.document_list.remove(self.current_document)

            facade = self.get_facade()
            facade.document_source.remove_document()

            self.current_document = ""
            self.contents = []

        pass
    
    def update_current_document(self, document_name: str, facade=None):
        self.current_document = document_name
        if not facade:
            facade = self.get_facade()
        self.update_content_list(facade)

    async def handle_upload_csv(self, files: list[rx.UploadFile]):
        """
            Handles the newly uploaded csv file
            try to refresh the content list
        """
        self.show_spin()

        for file in files:
            file_path = rx.get_upload_dir() / file.filename
            print("File Uploaded: ", file_path, file.filename)
            upload_data = await file.read()

            GPTAPIFacade.UploadCSV(upload_data, file.filename)

        self.hide_spin()


    def show_entry_embed_alert(self, status='success'):
        self.alert.open = True
        self.alert.message = 'Current Entry '
        self.alert.title = 'Embedding Current Entry'
        if status == 'success':
            self.alert.message = self.alert.message + ' successfully embedded'
        elif status == 'failed':
            self.alert.message = self.alert.message + ' embedding failed'

    def show_entry_delete_alert(self, status='success'):
        self.alert.open = True
        self.alert.message = 'Current Entry '
        self.alert.title = 'Deleted Current Entry'
        if status == 'success':
            self.alert.message = self.alert.message + ' successfully embedded'
        elif status == 'failed':
            self.alert.message = self.alert.message + ' embedding failed'

    def index_of_content(self, con: Content):
        for index, content in enumerate(self.contents):
            if content.title == con['title'] and content.text == con['text']:
                return index
        return -1

    def update_content_title(self, con: Content, event):
        try:
            idx = self.index_of_content(con)
            if idx > -1:
                self.contents[idx].edited_title = event
        except Exception as e:
            print(f"Error occured : {e}")
        
    def update_content_text(self, con: Content, event):
        try:
            idx = self.index_of_content(con)
            if idx > -1:
                self.contents[idx].edited_text = event
        except Exception as e:
            print(f"Error occured : {e}")

    def handle_collapsed(self, con: Content):
        try:
            idx = self.index_of_content(con)
            if idx > -1:
                self.contents[idx].collapsed = not self.contents[idx].collapsed
        except Exception as e:
            print(f"Error occured : {e}")

    def handle_entry_editing(self, con: Content):
        try:
            idx = self.index_of_content(con)
            print("edit", idx)
            if idx > -1:
                self.contents[idx].editing = not self.contents[idx].editing
        except Exception as e:
            print(f"Error occured : {e}")

    def handle_entry_delete(self, con: Content):
        self.show_spin()

        facade = self.get_facade()
        heading = Heading(title=con['edited_title']) # for embedding.
        heading.text = con['edited_text']
        # refactored existing calculate_embeddings with man-made heading.
        headingwithEmbedding = facade.calculate_embeddings_for_heading(heading) 

        try:
            document_source = facade.document_source
            for index, heading in enumerate(document_source.headings):
                if heading.title == con['title'] and heading.text == con['text']:
                    document_source.headings.remove(heading)
                    break

            document_source.save_to_csv()
            self.show_QA_embed_alert('success')
        except KeyError:
            print("error : no documents")
        
        try:
            for index, content in enumerate(self.contents):
                if content.title == con['title'] and content.text == con['text'] and content.vector == con['vector']:
                    self.contents.remove(content)
                    break
        except KeyError:
            print("error : no content like this")
        self.show_entry_delete_alert('success')
        print("Content Changed To: ", con)

        self.hide_spin()

    def handle_content_save(self, con: Content):
        """
            Handle event when 'save' button clicked on the expand mode of content
        """
        self.show_spin()

        self.handle_entry_editing(con)

        # Refactor to handle embedding heading

        facade = self.get_facade()
        heading = Heading(title=con['edited_title']) # for embedding.
        heading.text = con['edited_text']
        # refactored existing calculate_embeddings with man-made heading.
        headingwithEmbedding = facade.calculate_embeddings_for_heading(heading) 

        try:
            document_source = facade.document_source
            idx = -1
            for index, heading in enumerate(document_source.headings):
                if heading.title == con['title'] and heading.text == con['text']:
                    print(heading.title, heading.text, index)
                    idx = index
                    break

            if idx >= 0:
                # document_source.headings.append(headingwithEmbedding)
                print(len(self.contents), idx)


                document_source.headings[idx] = headingwithEmbedding
                document_source.save_to_csv()
                self.show_QA_embed_alert('success')
        except KeyError:
            print("error : no documents")
        
        try:
            for index, content in enumerate(self.contents):
                if content.title == con['title'] and content.text == con['text'] and content.vector == con['vector']:
                    self.contents[index].title = con['edited_title']
                    self.contents[index].text = con['edited_text']
                    break
        except KeyError:
            print("error : no content like this")
        self.show_entry_embed_alert('success')
        print("Content Changed To: ", con)
        
        self.hide_spin()

    def update_content_list(self, facade):
        self.show_spin()

        print("\n__________________ similar contents _____________ \n")
        print(facade.document_source.filepath)
        results = facade.get_similar_content(self.question, 9)
        self.contents = []
        for entry in results:
            print(type(entry['token']), entry['token'])
            content = Content(
                title=entry['title'],
                edited_title=entry['title'],
                text=entry['text'],
                edited_text=entry['text'],
                token=entry['token'],
                vector=entry['vector'],
                collapsed=True,
                editing=False)
            self.contents.append(content)
        #     yield

        self.hide_spin()

    # ////////////////////////////About Entry////////////////////////////

    # ------------------------About Rag------------------------

    def handle_raglimit_update(self):
        """
            handle Submit Rag Limit Button clicked
        """
        facade = self.get_facade()
        facade.update_request_token_len(self.rag_limit)

    def handle_ragresponse_update(self):
        """
            handle Submit Rag Response Button clicked
        """
        facade = self.get_facade()
        facade.update_response_token_len(self.rag_response)

    # ////////////////////////////About Rag////////////////////////////

    # ------------------------About Instruction------------------------

    def handle_instruction_update(self):
        """
            handle 'save' button clicked event in the instruction panel
        """
        facade = self.get_facade()
        facade.update_instruction_text(self.instruction)

    def handle_load_instruction(self):
        """
            handle 'load' button clicked event in the instruction panel
        """
        facade = self.get_facade()
        self.instruction = facade.load_instruction_from_file()

    # ///////////////////////////About Instruction///////////////////////////