from document import *
from GPT_API_Facade import GPTAPIFacade
from ast import literal_eval

#create a document source
"""document_source = SegmentableDocument('Agile Change')
document_source.load('Agile Change')  # Load the document
Heading.GLOBAL_HEADING_COLLAPSE_LEVEL(4)
document_source.save_to_csv()
document_source.save_to_file()"""

"""#generate tuning examples
document_source = SegmentableDocument('Agile Change')
document_source.load_from_csv()
facade = GPTAPIFacade(document_source=document_source)
results = facade.generate_tuning_examples(overwrite=True)
document = facade.data_source
document_source.save_to_csv() """


"""#tune a gpt model with examples
document_source = SegmentableDocument('Agile Change')
document_source.load_from_csv()
facade = GPTAPIFacade(document_source=document_source)
facade.tune_gpt_with_examples() """


# calculate and save embeddings
SegmentableDocument.GLOBAL_ROOT_FOLDER('C:\\dev\\reflex-chat-main\\data\\docs\\')
document_source = SegmentableDocument('Product Practice')
document_source.load()
facade = GPTAPIFacade(document_source=document_source)
facade.calculate_embeddings()
facade.document_source.save_to_csv()


"""#run a search from a previously prepared csv with embeddings
SegmentableDocument.GLOBAL_ROOT_FOLDER('D:/ai/Jeff GPT/tuning/reflex-chat-main/data')
document_source = SegmentableDocument('Agile Change')
document_source.load_from_csv()
facade = GPTAPIFacade(document_source=document_source)
#results = facade.search_documents('What is the best way to complete a change canvas?',50)
#print(results)  

response = facade.answer_with_gpt_4('What is the best way to complete a change canvas?')
response = facade.answer_with_gpt_4('What are the components?')
print(response)"""

"""
# load documents and save csvs for all files in a folder
SegmentableDocument.GLOBAL_ROOT_FOLDER('C:\\dev\\reflex-chat-main\\data\\docs')
folder =  DocumentFolder('/./')
folder.load()
folder.save_to_csv()

facade = GPTAPIFacade(document_source=folder)
facade.calculate_embeddings()
folder.save_to_csv()
print(facade.answer_with_gpt_4("What is Agile By Design's approach ?"))"""

"""#load csv from folder and chat

SegmentableDocument.GLOBAL_ROOT_FOLDER('D:/ai/GPT/tuning/reflex-chat-main/data')
folder =  DocumentFolder('./')
folder.load_from_csv()
facade = GPTAPIFacade(document_source=folder)
print(facade.answer_with_gpt_4('What is Agile By Designs approach ?'))"""

"""#load csv from folder and calculate embeddings
SegmentableDocument.GLOBAL_ROOT_FOLDER('D:/ai/Jeff GPT/tuning/reflex-chat-main/data')
folder =  DocumentFolder('./')
folder.load_from_csv()
facade = GPTAPIFacade(document_source=folder)
facade.calculate_embeddings()
folder.save_to_csv() """




