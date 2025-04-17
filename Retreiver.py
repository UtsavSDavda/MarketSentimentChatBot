import os
import pickle
import json
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.core.schema import TextNode
import streamlit as st
pickled_nodes = "nodes.pkl"
with open(pickled_nodes,'rb') as file:
    nodes = pickle.load(file)

Filtered_Nodes = []

open_ai_api_key = st.secrets["OPEN_AI"]

llm = OpenAI(api_key=open_ai_api_key,model="gpt-4o",temperature=0.2)

prompt_for_hard_filters = f"""You are assisting a news chatbot that uses metadata to filter and retrieve relevant articles. Each article is tagged with the following metadata fields: 'Brand names', 'Company names', 'Locations', 'People', 'Business sectors', 'Sentiment', 'publish_date', and 'Remarks'.

Given a user query, your task is to determine the hard filters by selecting both the metadata fields and the corresponding values.

Now, consider the following user query:

"{{user_query}}"

Based on this query, create a JSON object that contains the appropriate metadata fields and values to be used as hard filters. Only include fields and values that are critical for filtering the documents.
Strictly return only a JSON object in your response. Do not write even a single character except the JSON object in your response.

JSON Output:

"""
prompt_for_applying__hard_filters = f"""You are given a filter in a JSON format with various fields and various values in the field. You are given a metadata file.
For every field in the filter: If the field does not exist as a field in the metadata file return FAIL. If among all the values under the field are not there in the metadata file as values return FAIL.
If the above FAIL conditions do not match for any field return PASS. Do not be case sensitive. Only return PASS/FAIL and write nothing else in response.
Filter: '{{filter}}'.
Metadata File: '{{metadata_file}}'.
Answer (PASS/FAIL):

"""

prompt_for_keyword_filters = f""""""
prompt_for_react_agent = f"""You are given the role of a stock market and current affairs expert.You are given a query by a user and some tools. Create a filter to filter out the Nodes from our data based on the user's query, and filter all the Node objects using the filter you ahve created using your tools. From the filtered Nodes extract the text data and use an LLM to answer the user's query appropriately and return your response to the user.
User's query: {{user_query}}.

Your response:

"""


prompt_for_getting_answers = f"""YOu are stock market research and current affairs expert and are an assistant to the user. Answer the user's query and generate your answer strictly based on the context provided to you.
User's Query: '{{user_query}}'
Context: '{{context}}'

Assistant: 

"""
def hard_filter_function(user_query):
    """Returns the hard filters as a JSON object. Lets you know what values to put in the hard filter to extract relevant information."""
    hard_filters = llm.complete(prompt_for_hard_filters.format(user_query=user_query))
    return hard_filters

def retreive_node_data(Node:TextNode):
    """Returns the metadata of a single Node for examination"""
    return Node.metadata
            
def apply_filter_on_node(filter,nodetext):
    """This functions applies a Hard Filter on a Node metadata and returns PASS/FAIL. PASS means the Node has passed through this filter and FAIL means the Node has not passed through this filter."""
    response = llm.complete(prompt_for_applying__hard_filters.format(filter=filter,metadata_file=nodetext))
    return str(response)

def check_hard_all_nodes(filter):
    """This function checks all the Nodes with the filter provided and adds the filtered Nodes into a new list and returns the list."""
    for node in nodes:
        answer = apply_filter_on_node(filter,node.metadata)
        print(answer)
        if  answer == "PASS":
            Filtered_Nodes.append(node)
        elif answer == "FAIL":
            continue
        else:
            print("Confusing response from function.")

    return Filtered_Nodes

def Generate_Answer_From_Nodes(user_query):
    """Takes the list of the filtered Nodes and answers the user's query using the text data in them. It requires the original user query as an input."""
    context = ""
    for node in Filtered_Nodes:
        context+=(node.text)
        context+=("\n\n")
    response = llm.complete(prompt_for_getting_answers.format(user_query=user_query,context=context))
    return response

Create_Filter_tool = FunctionTool.from_defaults(fn=hard_filter_function)
Retreive_Node__MD_Tool = FunctionTool.from_defaults(fn=retreive_node_data)
Check_All_Node_Tool = FunctionTool.from_defaults(fn=check_hard_all_nodes)
Answer_Generative_Tool = FunctionTool.from_defaults(fn=Generate_Answer_From_Nodes)

chatter = ReActAgent.from_tools(tools=[Create_Filter_tool,Check_All_Node_Tool,Answer_Generative_Tool],llm=llm,verbose=True)
if query := st.chat_input("Ask about market-sentiments?"):
    st.chat_message("user").markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})
    response = chatter.chat(prompt_for_react_agent.format(user_query=query))
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})