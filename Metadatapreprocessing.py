import os
import pandas as pd
import pickle
import json
from datetime import datetime
from llama_index.core import Document
from llama_index.core.schema import MetadataMode 
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.storage.docstore import SimpleDocumentStore

open_ai_api_key = os.getenv("OPEN_AI")

llm = OpenAI(api_key=open_ai_api_key,model="gpt-4o",temperature=0.2)

List_of_Documents = []

prompt_for_agent = f"""Extract metadata from the following article. Use the available tools to:
                1. Extract entities (brand names, company names, locations, people)
                2. Identify the business sector(s) discussed
                3. Identify the sentiment in the article.
                Combine all the fields from all the above results into a single JSON object. Note that the JSON will just contain a list of individual fields and values/list of values and will not contain another JSON within it. 
                Return only the JSON object as a response.Do not write anything in the response except the JSON.

                Article: {{text}}

                JSON Output:

                """

entity_prompt = f"""Extract the following types of entities from the given text:
    1. Brand names
    2. Company names
    3. Locations
    4. People

    Return the results as a JSON object with these categories as keys and lists of extracted entities as values.

    Text: {{text}}

    JSON Output:"""

sector_prompt = f"""Identify the business sector(s) discussed in the following text. Choose from these categories:
    - Technology
    - Finance
    - Healthcare
    - Energy
    - Other (specify)

    Return the results as a JSON list of identified sectors.

    Text: {{text}}

    JSON Output:

    """
sentiment_prompt = f"""Analyze the sentiment of the given text regarding the financial/geopolitical situation. 
Also, find any underlying optimism or concerns about future trends. Return the response strictly in the form of a JSON list with following 2 fields in it:
 -Sentiment:The identified sentiment
 -Remarks:Any major underlying optimism or concerns. If nothing major just write None.
If you do not get a reasonable answer for any of the above fields return None in the value of that particular field.

    Text: {{text}}

    JSON Output:

    """
def get_entities(text):
    """Extracts various entities from the text."""
    response = llm.complete(entity_prompt.format(text=text))
    return response

def get_sector(text):
    """Finds out affected business sectors."""
    response = llm.complete(sector_prompt.format(text=text))
    return response

def get_sentiment(text):
    """Returns the sentiment of the text."""
    response = llm.complete(sentiment_prompt.format(text=text))
    return response

def create_entity_agent():

    EntityTool = FunctionTool.from_defaults(fn=get_entities)
    SectorTool = FunctionTool.from_defaults(fn=get_sector)
    SentimentTool = FunctionTool.from_defaults(fn=get_sentiment)
    EntityAGENT = ReActAgent.from_tools([EntityTool,SectorTool,SentimentTool],llm=llm,verbose=True)
    return EntityAGENT

EntityAGENT = create_entity_agent()

def one_text_metadata(text,EA: ReActAgent,time):
    response = EA.chat(prompt_for_agent.format(text=text))
    mdfortext = json.loads(str(response))
    print(mdfortext)
    doc = Document(text=text,metadata=mdfortext)
    doc.metadata["publish_date"] = time
    doc.excluded_embed_metadata_keys=(list(doc.metadata.keys()))
    return doc

def attach_md_row(row):
    merged_text = f"{row['Headlines']}: {row['Description']}"
    time = row['Time']
    iso_time = datetime.strptime(time, "%b %d %Y").strftime("%Y-%m-%d")
    print(iso_time)
    List_of_Documents.append(one_text_metadata(merged_text,EntityAGENT,iso_time))
    return

def attach_md_csv(location_of_csv):
    data = pd.read_csv(location_of_csv)
    data.head(15).apply(attach_md_row, axis=1)
    return

attach_md_csv('data/reuters_headlines.csv')

print("All documents MD created successfully.")

Doc_to_Node_Parser  = SimpleNodeParser.from_defaults()
List_of_Nodes = Doc_to_Node_Parser.get_nodes_from_documents(List_of_Documents)
pickle_file_path = 'nodes.pkl'
with open(pickle_file_path, 'wb') as file:
    pickle.dump(List_of_Nodes, file)
print("Nodes pickled successfully.")