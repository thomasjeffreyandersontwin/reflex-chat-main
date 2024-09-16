from lib2to3.fixes.fix_methodattrs import MAP

from openai import OpenAI
import json
import math

import os
import re

import pandas as pd
from scipy.spatial import distance  
import plotly.express as px

from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
import tiktoken
import numpy as np

from gpt.document import *

from umap import *
from ast import literal_eval

class GPTAPIFacade: 
    def __init__(self, document_source, segment_limit=1000, temperature=0.5):
        self.document_source = document_source   
        self.temperature = temperature
        self.tuning_instructions_file ='./data/prompt_build_instructions.txt'  
        self.instruction_text = ""
        self.chunk_processing_limit = 10000000000
        self.request_token_len = 4000
        self.response_token_len = 40000
        self.model = "gpt-4-turbo"
        
        self.client = OpenAI(api_key="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")
        self.searchableDataFrame = None
        
        self.initialize_message_history()

    def update_request_token_len(self, request_token_len):
        self.request_token_len = request_token_len

        print("Rag Limit Changed To: ", self.request_token_len)
        
    def update_response_token_len(self, response_token_len):
        self.response_token_len = response_token_len
        print("Rag Response Changed To: ", self.response_token_len)
     
    def initialize_message_history(self):
        # with open(SegmentableDocument.GLOBAL_ROOT_FOLDER() + '/prompt_agile_context.txt' , 'r') as file:
        #     prompt = file.read()
        
        self.message_history = [
                {"role" : "system", "content":""}
            ]    
        
    def insert_instruction_history(self):
        # with open(SegmentableDocument.GLOBAL_ROOT_FOLDER() + '/prompt_agile_context.txt' , 'r') as file:
            # prompt = file.read()
        if self.instruction_text != "":
            self.message_history = [
                {"role" : "system", "content":self.instruction_text}
            ]
            print("instruction replaced: ", self.instruction_text)

    def update_instruction_text(self, instruction_text):
        """
            Update instruction_test from ui value
            and call insert_instruction_history method
        """
        self.instruction_text = instruction_text
        self.save_instruction_to_file()
        self.insert_instruction_history()

    def load_instruction_from_file(self):
        with open(self.tuning_instructions_file, 'r') as file:
            self.instruction_text = file.read()
        return self.instruction_text

    def save_instruction_to_file(self):
        with open(self.tuning_instructions_file, 'w') as file:
            file.write(self.instruction_text)
        pass
    def generate_tuning_examples(self, overwrite):
        with open(self.tuning_instructions_file, 'r') as file:
            prompt = file.read()
        
        counter = 0
        completions=[]
   
        chunks =list(self.document_source.headings_iterator)
        for chunk in chunks:
           
            try:
                chat_completion = self.client.chat.completions.create(
                    model="gpt-3.5-turbo", # isnert instruction message
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": "**" + chunk.title + "**" + chunk.text}
                    ],
                    temperature=self.temperature
                )
                completion = chat_completion.choices[0].message.content
                print ("completion returned " + chat_completion.choices[0].message.content)
            except Exception as e:
                print(f"the OPENAI service failed for {chunk}")
                with open("error_log.txt", 'a', encoding='utf-8') as err_file:
                    err_file.write(f"Error in API Call for: {chunk}\n")
                    continue

            completion = completion.replace("\n", "").replace("\'", "'")
            completions.append(completion)
            
            json_strings = self.split_jsons(completion)

            for json_str in json_strings:
                result = self._validate_tuning_file(json_str)
                if result != False :
                    chunk.tuning_examples.append(result)
            counter += 1
            
            if counter > self.response_token_len:
                break
        return completions
    
    def split_jsons(self,json_string):
        # Split the concatenated JSON strings; assumes they're split by '}{' and that each JSON object is well-formed
        json_objects = re.split(r'(?<=})\s*(?={)', json_string)
        return json_objects
    
    @property
    def tuning_examples_split_across_testing_and_training(self):   
        tuning_examples = self.document_source.nested_tuning_examples 
        # Split and write to respective files
        return train_test_split(tuning_examples, test_size=0.2, random_state=42)  

    def _validate_tuning_file(self, line):
        try:
            # Ensure line ends correctly
            if line.strip().endswith("}]"):
                line += "}"
            # Check if each line is a valid JSON object
            data = json.loads(line)

            if 'messages' not in data:
                error = f"Missing 'messages' key for {line}"
                result = False
            for message in data['messages']:
                if 'role' not in message or 'content' not in message:
                    error = f"Missing 'role' or 'content' key in messages for {line}"
                    result = False
            result =  json.dumps(data)
        except json.JSONDecodeError as e:
            error =f"Invalid JSON for {line}: {str(e)}"
            result =  False

        
        if result!=False:
            system_message = "{\"role\":\"system\", \"content\":\" You Are Jeff Anderson!!! you are an Agile consulting expert. Embody Jeff's style—insightful, challenging conventional (Agile) thinking, and emphasizing an adaptive mindset over traditional Agile methods and methodology, promoting adaptability and a mindset focused on value creation over rigid methodologies.Maintain a knowledgeable tone, not afraid to challenge the status quo,  focus on promoting effective, human-centric approaches.\"}"
            system_message = json.loads(system_message)
            result = json.loads(result)
            result['messages'].append(system_message)
            result = json.dumps(result)
            return result
            chunk.tuning_example.append = completion
        else:
            print (error)
            with open("error_log.txt", 'a', encoding='utf-8') as err_file:
                err_file.write(f"Error in JSON: {line}\n")
                err_file.write(f"Error in JSON is: {error}\n\n")
            return False

    def tune_gpt_with_examples(self):
        
        training_example_file, validation_example_file =self.create_tuning_example_files_from_data_source()
        
        training_example_file_object = self.client.files.create(file = training_example_file, purpose="fine-tune")
        training_example_file_id = training_example_file_object.id

        validation_example_file_object = self.client.files.create(file = validation_example_file, purpose="fine-tune")
        validation_example_file_id = validation_example_file_object.id
        fine_tuning_job = self.client.fine_tuning.jobs.create(training_file=training_example_file_id,validation_file=validation_example_file_id,  model="gpt-3.5-turbo", suffix="jeff-agile")

        print("Fine-tuning job created successfully:", fine_tuning_job) 

    def create_tuning_example_files_from_data_source(self):
        training_example_file_path = self.document_source.name + '_training.jsonl'
        validation_example_file_path = self.document_source.name + '_validation.jsonl'
        if os.path.exists(training_example_file_path):
            os.remove(training_example_file_path)
        if os.path.exists(validation_example_file_path):
            os.remove(validation_example_file_path)
            
        
        tuning_examples = self.document_source.tuning_examples
        training_examples, validation_examples = train_test_split(tuning_examples, test_size=0.2, random_state=42)
        
        with open(training_example_file_path, 'w') as training_example_file:
            for example in training_examples:
                training_example_file.write(example + '\n')
        
        with open(validation_example_file_path, 'w') as validation_example_file:
            for example in validation_examples:
                validation_example_file.write(example + '\n')
    
        self.remove_empty_newlines( training_example_file_path)
        self.remove_empty_newlines( validation_example_file_path) 
        
        training_examples=open(training_example_file_path, "rb")
        validation_examples=open(validation_example_file_path, "rb")  
        return training_examples, validation_examples  

    def remove_empty_newlines(self, file_path):
    # Open the file and read lines
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Filter out empty newlines
        non_empty_lines = [line for line in lines if line.strip() != '']

        # Write the filtered lines back to the file
        with open(file_path, 'w') as file:
            file.writelines(non_empty_lines)
            
    def _is_all_caps(self, text):
        return text.isupper()
    
    def tune_gpt(self):
        training_examples, validation_examples = self.create_tuning_example_files_from_data_source()
        
        training_examples_object = self.client.files.create(file=open(training_examples, "rb"), purpose="fine-tune")
        training_examples_object_id = training_examples_object.id

        validation_examples_object = self.client.files.create(file=open(validation_examples, "rb"), purpose="fine-tune")
        validation_examples_object_id = validation_examples_object.id
        fine_tuning_job = self.client.fine_tuning.jobs.create(training_file=training_examples_object_id, validation_file=validation_examples_object_id,  model="gpt-3.5-turbo", suffix="jeff-agile")

        print("Fine-tuning job created successfully:", fine_tuning_job)       
 
    def get_embedding(self,text_to_embed):
        response = self.client.embeddings.create(
            model= "text-embedding-ada-002",
            input=[text_to_embed]
        )
        embedding = response.data[0].embedding
        return embedding
    
    def calculate_embeddings(self):
        #use document headibg iterator and then get full title and text from each heading
        for heading in self.document_source.headings_iterator:
            text_to_get_embedding_for = heading.full_title + heading.text
            heading.embedding = self.get_embedding(text_to_get_embedding_for)    
        
        self.document_source.createDataFrame()
        self.createSearchDataFrame()

    def calculate_embeddings_for_heading(self, heading: Heading):
        #use document headibg iterator and then get full title and text from each heading
        # text_to_get_embedding_for = heading.full_title + heading.text
        text_to_get_embedding_for = heading.title + heading.text

        heading.embedding = self.get_embedding(text_to_get_embedding_for)
        
        self.document_source.createDataFrame()
        self.createSearchDataFrame()

        return heading
    
    def calculate_embeddings_for_headings(self, headings: list[Heading]):
        #use document headibg iterator and then get full title and text from each heading
        for heading in headings:
            text_to_get_embedding_for = heading.title + heading.text
            heading.embedding = self.get_embedding(text_to_get_embedding_for)    
        
        self.document_source.createDataFrame()
        self.createSearchDataFrame()
        return headings

    def createSearchDataFrame(self):
        try:
            self.searchableDataFrame = self.document_source.dataFrame[
                self.document_source.dataFrame["Text"].apply(lambda x: isinstance(x, str) and x.strip() != "")
            ]
        except KeyError:
            print('self.document_source error', self.document_source.filepath)
        try:
            self.searchableDataFrame['Embedding'] = self.searchableDataFrame['Embedding'] .apply(
                lambda x: literal_eval(x) if isinstance(x, str) else x
            )
        except KeyError:
            print("Embedding column is missing. Adding it now.")
            self.searchableDataFrame['Embedding'] = None
    
    @property 
    def previous_user_messages(self):
        return [message['content'] for message in self.message_history if message['role'] == 'user']
    
    def perform_embedding_based_search(self, prompt, n):
        promptEmbedding = self.get_embedding(prompt)
        promptEmbedding = np.array(promptEmbedding).reshape(1, -1)
        user_embeddings = [self.get_embedding(content) for content in self.previous_user_messages]
        user_embeddings = [np.array(embedding).reshape(1, -1) for embedding in user_embeddings]

        #combine embeddings from user prompt and prevoius prompts
        all_embeddings = user_embeddings + [promptEmbedding]
        combined_embedding = np.mean(np.vstack(all_embeddings), axis=0).reshape(1, -1)

        if self.searchableDataFrame is None:
            self.createSearchDataFrame()
       
        try:
            self.searchableDataFrame['similarities'] = self.searchableDataFrame['Embedding'].apply(
                lambda x: cosine_similarity(np.array(x).reshape(1, -1), combined_embedding)[0][0]
            )
        except KeyError:
            print("error while initializing similarities")

        # Sort by similarities and return top n results
        return self.searchableDataFrame.sort_values(by='similarities', ascending=False).head(n)

    @property
    def embeddings(self):
        return self.document_source.embeddings
    
    def visualize_embedding_clusters(self):
        kmeans = KMeans(n_clusters=3)
        kmeans.fit(self.document_source.embeddings)
        # Perform dimensionality reduction on the embeddings
        umap = MAP()
        embeddings_2d = umap.fit_transform(self.embeddings)
        
        # Plot the clusters
        fig = px.scatter(x=embeddings_2d[:, 0], y=embeddings_2d[:, 1], color=kmeans.labels_)
        fig.show()

    def retrieve_and_augment_prompt(self, prompt):
        separator = "\n\n"  # This can be adjusted as needed
        separator_token_len = GPTAPIFacade.get_number_of_token(separator)
        total_token_length =  GPTAPIFacade.get_number_of_token(prompt)

        augmentedContent =""
        
        relevantContent = self.perform_embedding_based_search(prompt, 9)
        
        #Augment prompt with most relevant found content
        for index, row in relevantContent.iterrows():
            #to do this is shit I should be usng the Heading object not this crappy dataframe shit
            augmentation = row['Full Title'] 
            if not isinstance(row['Text'], float): 
                augmentation= augmentation + " " + row['Text'] 
                
            augmentation_token_len = GPTAPIFacade.get_number_of_token(augmentation)
            potential_token_length = total_token_length + augmentation_token_len + separator_token_len
            
            #add if under the token limit 
            if potential_token_length <  self.request_token_len:
                augmentedContent += separator + augmentation
                total_token_length += potential_token_length
            else:
                break
        prompt = "\n\n\n Context:" + augmentedContent +"\n\n\n Question :" + prompt + '\n\n --- \n\n + '
        return prompt, total_token_length
    
    def get_similar_content(self, prompt, n):
        separator = "\n\n"  # This can be adjusted as needed
        separator_token_len = GPTAPIFacade.get_number_of_token(separator)
        total_token_length =  GPTAPIFacade.get_number_of_token(prompt)

        augmentedContent =""
        
        relevantContent = self.perform_embedding_based_search(prompt, n)
        
        result_array = []
        #Augment prompt with most relevant found content
        for index, row in relevantContent.iterrows():
            result_entry={'title':'', 'text':'', 'token':'', 'vector':''}
            #to do this is shit I should be usng the Heading object not this crappy dataframe shit
            augmentation = row['Full Title'] 
            result_entry['title'] = row['Full Title'] 
            result_entry['text'] = row['Text'] 
            result_entry['token'] = row['Token Length']
            result_entry['vector'] = row['similarities']
            result_array.append(result_entry)
        return result_array
    
    
    ENC = tiktoken.encoding_for_model("gpt-4")
    @classmethod
    def get_number_of_token(cls, str):   
        return len( cls.ENC.encode(str))

    def update_model(self, model):
        self.model = model

    def answer_with_gpt_4(self, prompt: str) -> str:
        chat_messages = self.prep_gpt_4_answer(prompt)
        response = self.client.chat.completions.create(model=self.model, messages=chat_messages, temperature=0.0, stream=True, max_tokens=self.request_token_len)
        return response
    
    def prep_gpt_4_answer(self, prompt: str) -> str:
        augmented_prompt, section_length = self.retrieve_and_augment_prompt( prompt)
        print(augmented_prompt)
        
        chat_messages = self.message_history + [{"role" : "user", "content": augmented_prompt}]
        
        # Check if the total length of the messages are greater than the max_tokens if so, remove oldest messages until it is less than max_tokens
        chat_message_string = ' '.join([temp_message["role"] + " " + temp_message["content"] for temp_message in chat_messages])
        while GPTAPIFacade.get_number_of_token(chat_message_string) > self.response_token_len:
            self.message_history.pop(1)
            chat_messages.pop(1)
            
        
        return chat_messages
    
       
        
    def track_conversation(self, prompt, response_content):
        # response_content = response.choices[0].message.content
        self.message_history.append({"role" : "user", "content": prompt})
        self.message_history.append({"role" : "assistant", "content": response_content})

        return response_content
    
    
    Instance = None
    
    @classmethod
    def GetInstance(cls, document_name):
        if cls.Instance is None or not cls.Instance.document_source or cls.Instance.document_source and cls.Instance.document_source.filepath != document_name:
            SegmentableDocument.GLOBAL_ROOT_FOLDER('./data')
            folder =  DocumentFolder('./')
            individual_document = folder.get_document_by_name(document_name)
            print("start it")
            individual_document.load_from_csv()
            print("made it")
            cls.Instance = GPTAPIFacade(document_source=individual_document)
        return cls.Instance
    
    @classmethod
    def GetChatsInstance(cls):
        SegmentableDocument.GLOBAL_ROOT_FOLDER('./data')
        print("opening chts")
        folder =  DocumentFolder('/chats')
        print("opned chats")
        cls.Instance = GPTAPIFacade(document_source=folder)
        return cls.Instance
    
    @classmethod
    async def createNewDocument(cls, document_name):
        SegmentableDocument.GLOBAL_ROOT_FOLDER('./data')
        folder =  DocumentFolder('/.')
        individual_document = folder.create_document(document_name)
        individual_document.load_from_csv()
        cls.Instance = GPTAPIFacade(document_source=individual_document)
        return cls.Instance
    
    @classmethod
    async def createNewChatCSV(cls, document_name):
        SegmentableDocument.GLOBAL_ROOT_FOLDER('./data')
        folder =  DocumentFolder('/chats')
        individual_document = folder.create_chat_document(document_name)
        cls.Instance = GPTAPIFacade(document_source=individual_document)
        return cls.Instance

    @classmethod
    def retrieve_document_list(cls):
        doc_list = []
        SegmentableDocument.GLOBAL_ROOT_FOLDER('./data')
        folder =  DocumentFolder('/.')
        for document in folder.data_documents:
            doc_list.append(document.filepath)
        return doc_list
    
    
    @classmethod
    def UploadCSV(cls, data, filename):

        filename = './data/uploadedfiles/' + filename
        with open(filename, "wb") as uploaded_file:
            uploaded_file.write(data)
        pass
