from getpass import getpass
#HF_TOKEN = "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"
HF_TOKEN = "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"
from haystack.nodes import PreProcessor,PromptModel, PromptTemplate, PromptNode
from google.cloud import storage
import PyPDF2
from haystack import Document
from haystack.document_stores import InMemoryDocumentStore
from haystack import Pipeline
from haystack.nodes import BM25Retriever
import pprint
import nltk
import torch

def extract_text_from_pdf(pdf_path):
  text=""
  with open(pdf_path,"rb") as pdf_file:
    pdf_reader=PyPDF2.PdfReader(pdf_file)
    for page_num in range(len(pdf_reader.pages)):
      page=pdf_reader.pages[page_num]
      text += page.extract_text()
    doc=Document(
                content=text,
                meta={"pdf_path": pdf_path})
    return doc

def format_learning_goals_from_rag_output(rag_output):
    if rag_output is None:
      return "No rag_output"
    learning_goals = rag_output['results'][0]
    formatted_learning_goals = '\n'.join([f" \n{goal.strip()}" for goal in learning_goals.split('\n') if goal.strip()])

    return formatted_learning_goals

def run_rag_pipeline(docs):
    # Your RAG pipeline code here 
    #docs=[doc]
    processor =PreProcessor(
                clean_empty_lines=True,
                clean_whitespace=True,
                clean_header_footer=True,
                split_by="word",
                split_length=500,
                split_respect_sentence_boundary=True,
                split_overlap=0,
                language="it")

    preprocessed_docs=processor.process(docs)

    document_store= InMemoryDocumentStore(use_bm25=True)
    document_store.write_documents(preprocessed_docs)
    retriever=BM25Retriever(document_store, top_k=2)

    qa_template = PromptTemplate(prompt=
                                """Using only the information contained in the context,
                                answer only the question asked without adding suggestions of possible questions and answer exclusively in Italian.
                                If the answer cannot be deduced from the context, reply: I don't know because it is not relevant to the Context.
                                Context: {join(documents)};
                                Question: {query}""")

    prompt_node=PromptNode(
            model_name_or_path="mistralai/Mixtral-8x7B-Instruct-v0.1",
            api_key=HF_TOKEN,
            default_prompt_template=qa_template,
            max_length=500,
            model_kwargs={"model_max_length":5000})

    rag_pipeline=Pipeline()
    rag_pipeline.add_node(component=retriever, name="retriever", inputs=["Query"])
    rag_pipeline.add_node(component=prompt_node, name="prompt_node", inputs=["retriever"])
    # Return model output
    #model_output = "Sample model output"  # Replace with actual model output
    #def print_answer(out):
        #results = out["results"][0]
        #processed_output = results.replace("'", "").replace("\n", "").strip("()")
        #pprint.pprint(processed_output)
    #model_output=print_answer(rag_pipeline.run(query=query))
    return rag_pipeline

def process_output(rag_pipeline,query):
    rag_output = rag_pipeline.run(query=query)
    model_output = format_learning_goals_from_rag_output(rag_output)
    print(model_output)

    return model_output

#pdf_text=extract_text_from_pdf(pdf_file_path)

