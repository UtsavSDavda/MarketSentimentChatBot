# MarketSentimentChatBot
A chatbot that answers users query on live market news and provides sentiment-analysis and metadata labelling. Built using Llama-index

# How to run this app?

You just require to install Streamlit, Llama-index-core and Llama-index-llms via pip. You need to have an OPENAI API KEY. When you host the streamlit app on community cloud, you need to add the API KEY in Streamlit Secrets under Advanced Settings. If you want to host it locally add the API KEY in a .env file in your app directory and name the variable as OPEN_AI. make sure you replace the lines: open_ai_api_key = st.secrets["OPEN_AI"] with os.getenv("OPEN_AI"). 
The files metadataprocessing.py and newscollector.py can be run without streamlit just with python filename.py. Run these files before running retriever.py.
You need to then run this command on a terminal: streamlit run retriever.py

# What is this app?
This is a streamlit app that can act as a chatbot and answer user queries on various news articles. It also has the ability to do sentiment analysis and filter news articles by topics/keywords.
There are 3 parts in the app:

1. Part 1: News Collector. The collector python file will fetch news articles via an API call and store them locally in a csv.

2. Part 2: Metadata Processing. This part annotates EACH news articles by addding MetaData to the object. The Metadata includes entities, sectors and sentiment. This is done via LLM calls. There are FunctionTool objects to do each of the tasks, and there is a Llama-index agent equipped with those tools. The News article text is converted into a Document object. We can add Metadata in a Document object. Then we pickle the data after converting the Documents into Nodes.

3. Part 3: Retriever. This part is the one that faces the user and inputs user queries. We pass the user query to a prompt that figures out HOW to filter the available data to answer the query based on it's relevance. The output will be a set of filters to apply on the metadata of each article (Now a Node object). Next, we filter out the data and gain our context for answering the queries. We take the top K nodes and use the articles to answer the user's query by another LLM call. All of this is achieved by creating an agent and appending various FunctionTools that can each perform a single task in the process. 
