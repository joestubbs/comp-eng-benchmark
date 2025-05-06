### Run Graph-Vector RAG application 

## Graph Database - neo4j

Start a local instance of neo4j community:

```
docker run \
    --publish=7477:7474 --publish=7699:7687 \
    --volume=$HOME/neo4j/data:/data \
    -e NEO4J_apoc_export_file_enabled=true \
    -e NEO4J_apoc_import_file_enabled=true \
    -e NEO4J_apoc_import_file_use__neo4j__config=true \
    -e NEO4J_PLUGINS=\[\"apoc\",\"apoc-extended\"\,\"genai\"] \
neo4j

```

## LLMSHERPA - PDF Parsing
### Run llmsherpa locally  
Get the docker image: 
````
docker pull ghcr.io/nlmatics/nlm-ingestor:latest
````
Run the docker image:
````
docker run -p 5010:5001 ghcr.io/nlmatics/nlm-ingestor:latest
````
Your llmsherpa_url will be: "http://localhost:5010/api/parseDocument?renderFormat=all"

Reference: [llmsherpa](https://github.com/nlmatics/nlm-ingestor)


## Project Installations
### poetry shell
If poetry shell is not there, pip install the shell plugin
````
 pip install poetry-plugin-shell
````
### Start the poetry shell

``
poetry shell
``
### Install the project dependencies
```
poetry install --no-root
```

## Knowledge Graph - Vector - RAG App 
### Configuration 
#### .env
Copy .env_example to .env and fill in the actual values.
#### app_config.py
Configure the application in the app_config.py file.

### Create KG
```
python create_kg_from_pdf
```
### Create Embedding

```
python create_embedding
```
### Chat With Graph
```
python qa_entry
```
