import os
from dotenv import load_dotenv

# load .env file to environment
load_dotenv('.env', override=True)

### get all the environement variables
NEO4J_URL = os.getenv('NEO4J_URL')
NEO4J_DATABASE = os.getenv('NEO4J_DATABASE')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LLMSHERPA_API_URL = "http://localhost:5010/api/parseDocument?renderFormat=all"

config = {
    "neo4j_url": NEO4J_URL,
    "neo4j_user": NEO4J_USER,
    "neo4j_password": NEO4J_PASSWORD,
    "neo4j_database": NEO4J_DATABASE,
    "llm_provider": "ollama", #ollama
    "llm_name": "llama3.1:8b", # llama3.3
    "llm_base_url": "https://ollama.pods.tacc.develop.tapis.io", # "" of local Ollama https://api.openai.com/v1
    "embedding": {"model": "mxbai-embed-large", #  text-embedding-3-large
                  "dimension": 1024, # 3072
                  "similarity": "cosine",
                  "node_label": "Embedding"
                 },
    "source_rag":{"type":"pdf", 
                  "conf":{
                            "llmsherpa_api_url": LLMSHERPA_API_URL,
                            "pdf_file": "/home/jstubbs/gits/ml-and-kgs/all-rag-techniques/tapis/data/tapis2pdf_SHORT.pdf"
                  }},
   # "source_rag":{"type":"graph", 
   #                "conf":{}}
   "vector_index_on_node":"Chunk",
   "vector_index_name":"chunkVectorIndex"     
}