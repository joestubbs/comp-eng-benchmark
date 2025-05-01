import os
from dotenv import load_dotenv


# Common data processing
import json
import textwrap
import uuid
import hashlib

# Neo4j
from neo4j import GraphDatabase

# App config
from app_config import config
from create_embeddings import *

# Warning control
import warnings
warnings.filterwarnings("ignore")

# Langchain
from langchain_community.graphs import Neo4jGraph
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Neo4jVector
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain import hub

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

def get_llm_for_provider(provider):
    """
    Returns the LLM for this graph.
    """
    
    if provider=="openai":
       llm = ChatOpenAI(
           model=config["llm_name"],
           temperature=0,
           max_tokens=None,
           timeout=None,
           max_retries=2)
    else:
       llm = ChatOllama(model=config["llm_name"], temperature=0)
    return llm


def get_retrival_query_for_docs(embedding_node_label):
    retrieval_query="""
    WITH node, score MATCH (ch:Chunk)-[:HAS_EMBEDDING]->(node:Embedding)
    WITH ch,score MATCH (ch:Chunk) -[:HAS_PARENT]->(s:Section)
    RETURN ch.sentences as text, score,{source:s.title} as metadata
    """
    return retrieval_query


def set_kg_vector_store(text_node_property):
    embeddings = get_embedding_for_provider()
    
    kg_vector_store = Neo4jVector.from_existing_index(
    embedding=embeddings,
    url = config["neo4j_url"],
    username=config["neo4j_user"],
    password=config["neo4j_password"],
    database=config["neo4j_database"],  # neo4j by default
    index_name=config["vector_index_name"],  # chunkVectorIndex by default
    node_label=config["embedding"]["node_label"], # default"Embedding"
    embedding_node_property="value",  # embedding value property
    text_node_property="sentences" ,    #"sentences",  # text by default
    retrieval_query=get_retrival_query_for_docs(config["embedding"]["node_label"])
    )
    return kg_vector_store 

def get_vectorstore_as_retriever(kg_vector_store):
    return kg_vector_store.as_retriever(search_kwargs={"k": 25})


def qa_with_source(text_node_property):
    
    kg_vector_store = set_kg_vector_store(text_node_property)

    llm_provider = config["llm_provider"]


    general_system_template = """
    Use the following context to answer the question at the end.
    Make sure not to make any changes to the context if possible when prepare answers  so as to provide accuate responses.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    ----
    {summaries}
    ----
    At the end of each answer you should contain metadata for relevant document in the form of (source, page).
    """
    general_user_template = "Question:```{question}```"
    messages = [
        SystemMessagePromptTemplate.from_template(general_system_template),
        HumanMessagePromptTemplate.from_template(general_user_template),
        ]
    qa_prompt = ChatPromptTemplate.from_messages(messages)
    
    qa_chain = load_qa_with_sources_chain(
        get_llm_for_provider(llm_provider),
        chain_type="stuff",
        prompt=qa_prompt,
        )
    chain_with_retriever = RetrievalQAWithSourcesChain(
        combine_documents_chain = qa_chain,
        retriever = get_vectorstore_as_retriever(kg_vector_store),
        reduce_k_below_max_tokens = False,
        max_tokens_limit = 7000,      # gpt-4
    )

    return chain_with_retriever    

def qa_with_source1(text_node_property):
    
    kg_vector_store = set_kg_vector_store(text_node_property)

    llm_provider = config["llm_provider"]


    general_system_template = """
    Use the following context to answer the question at the end.
    Make sure not to make any changes to the context if possible when prepare answers  so as to provide accuate responses.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    ----
    {context}
    ----
    At the end of each answer you should contain metadata for relevant document in the form of (source, page).
    
    """
    general_user_template = "Question:```{input}```"
    messages = [
        SystemMessagePromptTemplate.from_template(general_system_template),
        HumanMessagePromptTemplate.from_template(general_user_template),
        ]
    qa_prompt = ChatPromptTemplate.from_messages(messages)
    question_answer_chain = create_stuff_documents_chain(get_llm_for_provider(llm_provider), qa_prompt)
    chain_with_retriever = create_retrieval_chain(get_vectorstore_as_retriever(kg_vector_store), question_answer_chain)
    return chain_with_retriever    
    
def qa_with_source2(text_node_property):
    
    kg_vector_store = set_kg_vector_store(text_node_property)
    llm_provider = config["llm_provider"]
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    combine_docs_chain = create_stuff_documents_chain(get_llm_for_provider(llm_provider), retrieval_qa_chat_prompt)
    retrieval_chain = create_retrieval_chain(get_vectorstore_as_retriever(kg_vector_store), combine_docs_chain)

    return retrieval_chain 
      


