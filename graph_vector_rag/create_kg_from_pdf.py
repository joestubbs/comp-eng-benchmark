#### This program uses significant code from https://github.com/Joshua-Yu/graph-rag/blob/main/openai%2Bllmsherpa/LayoutPDFReader_KGLoader.ipynb
#### to create Knowledgegraph from a pdf a document
#### This program follows as design as implemented in the above link and described in the blog: 
#### https://neo4j.com/blog/developer/graph-llm-rag-application-pdf-documents/
import os
from dotenv import load_dotenv
from datetime import datetime
import time

# Common data processing
import json
import textwrap
import uuid
import hashlib

# Neo4j
from neo4j import GraphDatabase

#llmsherpa
from llmsherpa.readers import LayoutPDFReader

# App config
from app_config import *

# Warning control
import warnings
warnings.filterwarnings("ignore")

#reload(config)

cypher_pool = [
        # 0 - Document
        "MERGE (d:Document {url_hash: $doc_url_hash_val}) ON CREATE SET d.url = $doc_url_val RETURN d;",  
        # 1 - Section
        "MERGE (p:Section {key: $doc_url_hash_val+'|'+$block_idx_val+'|'+$title_hash_val}) ON CREATE SET p.page_idx = $page_idx_val, p.title_hash = $title_hash_val, p.block_idx = $block_idx_val, p.title = $title_val, p.tag = $tag_val, p.level = $level_val RETURN p;",
        # 2 - Link Section with the Document
        "MATCH (d:Document {url_hash: $doc_url_hash_val}) MATCH (s:Section {key: $doc_url_hash_val+'|'+$block_idx_val+'|'+$title_hash_val}) MERGE (d)<-[:HAS_DOCUMENT]-(s);",
        # 3 - Link Section with a parent section
        "MATCH (s1:Section {key: $doc_url_hash_val+'|'+$parent_block_idx_val+'|'+$parent_title_hash_val}) MATCH (s2:Section {key: $doc_url_hash_val+'|'+$block_idx_val+'|'+$title_hash_val}) MERGE (s1)<-[:UNDER_SECTION]-(s2);",
        # 4 - Chunk
        "MERGE (c:Chunk {key: $doc_url_hash_val+'|'+$block_idx_val+'|'+$sentences_hash_val}) ON CREATE SET c.sentences = $sentences_val, c.sentences_hash = $sentences_hash_val, c.block_idx = $block_idx_val, c.page_idx = $page_idx_val, c.tag = $tag_val, c.level = $level_val RETURN c;",
        # 5 - Link Chunk to Section
        "MATCH (c:Chunk {key: $doc_url_hash_val+'|'+$block_idx_val+'|'+$sentences_hash_val}) MATCH (s:Section {key:$doc_url_hash_val+'|'+$parent_block_idx_val+'|'+$parent_hash_val}) MERGE (s)<-[:HAS_PARENT]-(c);",
        # 6 - Table
        "MERGE (t:Table {key: $doc_url_hash_val+'|'+$block_idx_val+'|'+$name_val}) ON CREATE SET t.name = $name_val, t.doc_url_hash = $doc_url_hash_val, t.block_idx = $block_idx_val, t.page_idx = $page_idx_val, t.html = $html_val, t.rows = $rows_val RETURN t;",
        # 7 - Link Table to Section
        "MATCH (t:Table {key: $doc_url_hash_val+'|'+$block_idx_val+'|'+$name_val}) MATCH (s:Section {key: $doc_url_hash_val+'|'+$parent_block_idx_val+'|'+$parent_hash_val}) MERGE (s)<-[:HAS_PARENT]-(t);",
        # 8 - Link Table to Document if no parent section
        "MATCH (t:Table {key: $doc_url_hash_val+'|'+$block_idx_val+'|'+$name_val}) MATCH (s:Document {url_hash: $doc_url_hash_val}) MERGE (s)<-[:HAS_PARENT]-(t);"
    ]
    

### initialize NEO4J instance
def initialiseNeo4j():
    print("Initializing Neo4j ----")
    cypher_schema = [
        "CREATE CONSTRAINT sectionKey IF NOT EXISTS FOR (c:Section) REQUIRE (c.key) IS UNIQUE;",
        "CREATE CONSTRAINT chunkKey IF NOT EXISTS FOR (c:Chunk) REQUIRE (c.key) IS UNIQUE;",
        "CREATE CONSTRAINT documentKey IF NOT EXISTS FOR (c:Document) REQUIRE (c.url_hash) IS UNIQUE;",
        "CREATE CONSTRAINT tableKey IF NOT EXISTS FOR (c:Table) REQUIRE (c.key) IS UNIQUE;",
       # "CALL db.index.vector.createNodeIndex('chunkVectorIndex', 'Embedding', 'value', 1536, 'COSINE');" 
        #"CALL db.index.vector.createNodeIndex('chunkVectorIndex', 'Embedding', 'value', 3072, 'COSINE');" # 3072 dimensions is for the newest 
        #openai embedding model, we have to make it 1536 for 
       # "CREATE VECTOR INDEX chunkVectorIndex IF NOT EXISTS FOR (c:Chunk) ON m.Embedding OPTIONS { indexConfig: { 'vector.dimensions':3072,'vector.similarity_function': 'cosine'}}
    ]
    print("config[\"neo4j_url\"]=" + config["neo4j_url"])
    print()
    driver = GraphDatabase.driver(uri=config["neo4j_url"], database=config["neo4j_database"], auth=(config["neo4j_user"], config["neo4j_password"]))

    with driver.session() as session:
        for cypher in cypher_schema:
            session.run(cypher)
    driver.close()

def create_section_nodes(session,doc, doc_url_hash_val):
    countSection = 0
    for sec in doc.sections():
        sec_title_val = sec.title
        sec_title_hash_val = hashlib.md5(sec_title_val.encode("utf-8")).hexdigest()
        sec_tag_val = sec.tag
        sec_level_val = sec.level
        sec_page_idx_val = sec.page_idx
        sec_block_idx_val = sec.block_idx

        # MERGE section node
        if not sec_tag_val == 'table':
            cypher = cypher_pool[1]
            session.run(cypher, page_idx_val=sec_page_idx_val
                        , title_hash_val=sec_title_hash_val
                        , title_val=sec_title_val
                        , tag_val=sec_tag_val
                        , level_val=sec_level_val
                        , block_idx_val=sec_block_idx_val
                        , doc_url_hash_val=doc_url_hash_val
                        )

            # Link Section with a parent section or Document

            sec_parent_val = str(sec.parent.to_text())

            if sec_parent_val == "None":    # use Document as parent
                cypher = cypher_pool[2]
                session.run(cypher, page_idx_val=sec_page_idx_val
                            , title_hash_val=sec_title_hash_val
                            , doc_url_hash_val=doc_url_hash_val
                            , block_idx_val=sec_block_idx_val
                            )

            else:   # use parent section
                sec_parent_title_hash_val = hashlib.md5(sec_parent_val.encode("utf-8")).hexdigest()
                sec_parent_page_idx_val = sec.parent.page_idx
                sec_parent_block_idx_val = sec.parent.block_idx

                cypher = cypher_pool[3]
                session.run(cypher, page_idx_val=sec_page_idx_val
                            , title_hash_val=sec_title_hash_val
                            , block_idx_val=sec_block_idx_val
                            , parent_page_idx_val=sec_parent_page_idx_val
                            , parent_title_hash_val=sec_parent_title_hash_val
                            , parent_block_idx_val=sec_parent_block_idx_val
                            , doc_url_hash_val=doc_url_hash_val
                            )
            # **** if sec_parent_val == "None":    

            countSection += 1
    return countSection

# 3 - Create Chunk nodes from chunks
def create_chunk_nodes(session, doc, doc_url_hash_val):
          
    countChunk = 0
    for chk in doc.chunks():
        chunk_block_idx_val = chk.block_idx
        chunk_page_idx_val = chk.page_idx
        chunk_tag_val = chk.tag
        chunk_level_val = chk.level
        chunk_sentences = "\n".join(chk.sentences)
    
        # MERGE Chunk node
        if not chunk_tag_val == 'table':
            chunk_sentences_hash_val = hashlib.md5(chunk_sentences.encode("utf-8")).hexdigest()
    
            # MERGE chunk node
            cypher = cypher_pool[4]
            session.run(cypher, sentences_hash_val=chunk_sentences_hash_val
                            , sentences_val=chunk_sentences
                            , block_idx_val=chunk_block_idx_val
                            , page_idx_val=chunk_page_idx_val
                            , tag_val=chunk_tag_val
                            , level_val=chunk_level_val
                            , doc_url_hash_val=doc_url_hash_val
                        )
        
            # Link chunk with a section
            # Chunk always has a parent section 
    
            chk_parent_val = str(chk.parent.to_text())
            
            if not chk_parent_val == "None":
                chk_parent_hash_val = hashlib.md5(chk_parent_val.encode("utf-8")).hexdigest()
                chk_parent_page_idx_val = chk.parent.page_idx
                chk_parent_block_idx_val = chk.parent.block_idx
    
                cypher = cypher_pool[5]
                session.run(cypher, sentences_hash_val=chunk_sentences_hash_val
                                , block_idx_val=chunk_block_idx_val
                                , parent_hash_val=chk_parent_hash_val
                                , parent_block_idx_val=chk_parent_block_idx_val
                                , doc_url_hash_val=doc_url_hash_val
                            )
                # Link sentence 
            #   >> TO DO for smaller token length
    
            countChunk += 1
    return countChunk

def create_table_node(session, doc, doc_url_hash_val):
 # 4 - Create Table nodes

    countTable = 0
    for tb in doc.tables():
        page_idx_val = tb.page_idx
        block_idx_val = tb.block_idx
        name_val = 'block#' + str(block_idx_val) + '_' + tb.name
        html_val = tb.to_html()
        rows_val = len(tb.rows)

        # MERGE table node

        cypher = cypher_pool[6]
        session.run(cypher, block_idx_val=block_idx_val
                        , page_idx_val=page_idx_val
                        , name_val=name_val
                        , html_val=html_val
                        , rows_val=rows_val
                        , doc_url_hash_val=doc_url_hash_val
                    )
        
        # Link table with a section
        # Table always has a parent section 

        table_parent_val = str(tb.parent.to_text())
        
        if not table_parent_val == "None":
            table_parent_hash_val = hashlib.md5(table_parent_val.encode("utf-8")).hexdigest()
            table_parent_page_idx_val = tb.parent.page_idx
            table_parent_block_idx_val = tb.parent.block_idx

            cypher = cypher_pool[7]
            session.run(cypher, name_val=name_val
                            , block_idx_val=block_idx_val
                            , parent_page_idx_val=table_parent_page_idx_val
                            , parent_hash_val=table_parent_hash_val
                            , parent_block_idx_val=table_parent_block_idx_val
                            , doc_url_hash_val=doc_url_hash_val
                        )

        else:   # link table to Document
            cypher = cypher_pool[8]  
            cypher = cypher_pool[8]
            session.run(cypher, name_val=name_val
                            , block_idx_val=block_idx_val
                            , doc_url_hash_val=doc_url_hash_val
                        )
        countTable += 1

    # **** for tb in doc.tables():
    
    return countTable

def link_chunks(session, doc, doc_url_hash_val):
    
    result = session.run(f"Match (s:Section) RETURN s.title As title, s.block_idx as block_idx")
    ch_list = []
    for record in result:
            sec_title = record["title"]
            cypher =  "MATCH (ch:Chunk) -[:HAS_PARENT]-> (s:Section) where s.title= $sec_title WITH ch ORDER BY ch.block_idx ASC WITH collect(ch) as ch_list CALL apoc.nodes.link(ch_list, \"NEXT\") RETURN size(ch_list)"       
            chunk_list_size = session.run(cypher)   
            ch_list.append(cypher)
            cypher_first = "MATCH (ch:Chunk) -[:HAS_PARENT]-> (s:Section) where s.title=$sec_title AND (ch:Chunk) -[:NEXT]->(:Chunk) RETURN ch"
            ch = session.run(cypher_first)             
        
   
    
def ingestDocumentNeo4j(doc, doc_location):

    driver = GraphDatabase.driver(uri=config["neo4j_url"], database=config["neo4j_database"], auth=(config["neo4j_user"], config["neo4j_password"]))

    with driver.session() as session:
        #cypher = ""

        # 1 - Create Document node
        doc_url_val = doc_location
        doc_url_hash_val = hashlib.md5(doc_url_val.encode("utf-8")).hexdigest()

        cypher = cypher_pool[0]
        session.run(cypher, doc_url_hash_val=doc_url_hash_val, doc_url_val=doc_url_val)    
        # 2 - Create Section nodes
        countSection = create_section_nodes(session, doc, doc_url_hash_val)
        countChunk = create_chunk_nodes(session, doc, doc_url_hash_val)
        countTable = create_table_node(session, doc, doc_url_hash_val)
        
        print(f'\'{doc_url_val}\' Done! Summary: ')
        print('#Sections: ' + str(countSection))
        print('#Chunks: ' + str(countChunk))
        print('#Tables: ' + str(countTable))

    driver.close()

def parse_pdf(llmsherpa_api_url,pdf_file):
    
    #Absolute path for the document
    #pdf_file= '/Users/spadhy/git-repos/documentation/source/technical/security.pdf' 
    #pdf_file = "/Users/spadhy/git-repos/documentation/source/technical/tapis2pdf_SHORT.pdf"
    pdf_reader = LayoutPDFReader(llmsherpa_api_url)

    # parse documents and create graph
    startTime = datetime.now()

    # read the pdf file
    doc = pdf_reader.read_pdf(pdf_file)

    # find the first / in pdf_file from right
    idx = pdf_file.rfind('/')
    pdf_file_name = pdf_file[idx+1:]
    # open a local file to write the JSON
    with open(pdf_file_name + '.json', 'w') as f:
        # convert doc.json from a list to string
        f.write(str(doc.json))
    
    
    print(f'Total time: {datetime.now() - startTime}')
    return doc



if __name__ == '__main__':
    if config["source_rag"]["type"] == "pdf":
        llmsherpa_api_url = config["source_rag"]["conf"]["llmsherpa_api_url"]
        pdf_file = config["source_rag"]["conf"]["pdf_file"]
        initialiseNeo4j()
        docs = parse_pdf(llmsherpa_api_url,pdf_file)
        ingestDocumentNeo4j(docs, pdf_file)
    else:
        print("Skip the KG creation. Graph already exists")
####
