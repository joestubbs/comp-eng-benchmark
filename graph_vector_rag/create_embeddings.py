import os
from dotenv import load_dotenv

# Neo4j
import neo4j
from neo4j import GraphDatabase

# Langchain
from langchain_community.graphs import Neo4jGraph
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
# Open AI
#from openai import OpenAI


# App config
from app_config import config

"""
LoadEmbedding: call LLM provider embedding API to generate embeddings for each property of node in Neo4j
"""

#EMBEDDING_MODEL = "text-embedding-3-large" #"text-embedding-ada-002"
#DEFAULT_EMBEDDING

#driver = GraphDatabase.driver(uri=config["neo4j_url"], database=config["neo4j_database"], auth=(config["neo4j_user"], config["neo4j_password"]))


# def get_embedding(client, text, model):
#     response = client.embeddings.create(
#                     input=text,
#                     model=model,
#                 )
#     return response.data[0].embedding

def get_embedding_for_provider():
    """
        Returns the embedding model used for this pipeline
    """
    if config["llm_provider"]=="openai":
        embeddings = OpenAIEmbeddings(model=config["embedding"]["model"])
    else:
        embeddings = OllamaEmbeddings(model=config["embedding"]["model"], base_url=config['llm_base_url'])
    return embeddings

def initializeVectorIndex():
    vector_index = config["vector_index_name"]
    vector_index_on_node = config["vector_index_on_node"]
    embedding_nodel_label = config["embedding"]["node_label"]
    dimension = config["embedding"]["dimension"]
    similarity_fn = config["embedding"]["similarity"]
    driver = GraphDatabase.driver(uri=config["neo4j_url"], database=config["neo4j_database"], auth=(config["neo4j_user"], config["neo4j_password"]))

    with driver.session() as session:
        #cypher = "CREATE VECTOR INDEX " + vector_index + " IF NOT EXISTS FOR (c:" +vector_index_on_node+") ON c."+ embedding_nodel_label +" OPTIONS { indexConfig: { `vector.dimensions`:"+ str(dimension)+ ",`vector.similarity_function`:'"+ similarity_fn+"'}};"
        #  TODO -- looks like some values are hard-coded here in the cypher, need to review...
        cypher = f"CALL db.index.vector.createNodeIndex('chunkVectorIndex', 'Embedding', 'value', { dimension }, 'COSINE');"
        print("cypher ===  " + cypher)
        try:
            session.run(cypher)
        except neo4j.exceptions.ClientError as e:
            if hasattr(e, "message"):
                if "equivalent index already exists" in e.message:
                    print(f"Got duplicate index error; ignoring...")
            else:
                print(f"Got unrecognized neo4j exception: {e}")
                raise e 

        driver.close()


def create_embeddings_pdf(property):
    
    vector_index_on_node = config["vector_index_on_node"]
    embedding_nodel_label = config["embedding"]["node_label"]
    embedding_model = config["embedding"]["model"]
        
    #openai_client = OpenAI (api_key = OPENAI_API_KEY)
    driver = GraphDatabase.driver(uri=config["neo4j_url"], database=config["neo4j_database"], auth=(config["neo4j_user"], config["neo4j_password"]))
    with driver.session() as session:
        # get chunks in document, together with their section titles
        result = session.run(f"MATCH (ch:Chunk) -[:HAS_PARENT]-> (s:Section) RETURN elementId(ch) AS id, s.title + ' >> ' + ch.{property} AS text")
        
        # create embeddings for the property of a node 
        # for each node, update the embedding property
        count = 0
        for record in result:
            id = record["id"]
            text = record["text"]
            
            # For better performance, text can be batched
            #embedding = get_embedding(openai_client, text, embedding_model) ## <-- embedding  model
            embeddings = get_embedding_for_provider()
            embedding = embeddings.embed_query(text)
            
            # key property of Embedding node differentiates different embeddings
            cypher = "CREATE (e:Embedding) SET e.key=$key, e.value=$embedding"
            cypher = cypher + " WITH e MATCH (n) WHERE elementId(n) = $id CREATE (n) -[:HAS_EMBEDDING]-> (e)"
            session.run(cypher,key=property, embedding=embedding, id=id )
            count = count + 1

        session.close()
        
        print("Processed " + str(count) + " " + "Chunk" + " nodes for property @" + property + ".")
        return count


def create_embeddings_pdf(label, property):
    vector_index_on_node = config["vector_index_on_node"]
    embedding_nodel_label = config["embedding"]["node_label"]
    embedding_model = config["embedding"]["model"]

    # openai_client = OpenAI (api_key = OPENAI_API_KEY)
    driver = GraphDatabase.driver(uri=config["neo4j_url"], database=config["neo4j_database"],
                                  auth=(config["neo4j_user"], config["neo4j_password"]))
    with driver.session() as session:
        # get chunks in document, together with their section titles
        result = session.run(
            f"MATCH (ch:{label}) -[:HAS_PARENT]-> (s:Section) RETURN elementId(ch) AS id, s.title + ' >> ' + ch.{property} AS text")

        # create embeddings for the property of a node
        # for each node, update the embedding property
        count = 0
        for record in result:
            id = record["id"]
            text = record["text"]

            # For better performance, text can be batched
            # embedding = get_embedding(openai_client, text, embedding_model) ## <-- embedding  model
            embeddings = get_embedding_for_provider()
            embedding = embeddings.embed_query(text)

            # key property of Embedding node differentiates different embeddings
            cypher = "CREATE (e:Embedding) SET e.key=$key, e.value=$embedding"
            cypher = cypher + " WITH e MATCH (n) WHERE elementId(n) = $id CREATE (n) -[:HAS_EMBEDDING]-> (e)"
            session.run(cypher, key=property, embedding=embedding, id=id)
            count = count + 1

        session.close()

        print("Processed " + str(count) + " " + "Chunk" + " nodes for property @" + property + ".")
        return count

if __name__ == '__main__':
        
     initializeVectorIndex()
     #create_embeddings_pdf("sentences")
     create_embeddings_pdf("Chunk","sentences")
     create_embeddings_pdf("Table", "name")
    