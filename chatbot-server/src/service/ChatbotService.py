import json
import logging
import os
import uuid
from urllib.parse import quote_plus

import cohere
import requests.exceptions
from agent.SearchAgent import SearchAgent
from dotenv import load_dotenv, find_dotenv
from groq import Groq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.sqlite import SqliteSaver
from pymongo import MongoClient
from service.VectorStoreService import VectorStoreService
from tavily import TavilyHybridClient, TavilyClient
from text.PromptMessage import PromptMessage
from text.WebURLs import WebURLs
from util.util import Util


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class ChatbotService:

    def __init__(self):
        self.template = None
        self.client = None
        self.llm_model = None
        self.embedding_model = None
        self.retrievers = None
        self.tools = None
        self.thread_id = str(uuid.uuid4())

    def query_groq_api(self, client, prompt, model):
        """Query the Groq API directly and return the response."""
        try:
            if not isinstance(prompt, str):
                raise ValueError(f"Prompt must be a string, but got {type(prompt)}")

            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                temperature=0.5,
                max_tokens=1024,
                stop=None,
                stream=False,
            )

            return response.choices[0].message.content

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error occurred: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")

    def is_query_relevant(self, query):
        """Check if the query is relevant to the prompt template using the model."""
        relevance_prompt = (
            f"This is prompt template : \"{self.template}\". Evaluate whether the following query is relevant to the prompt template: \"{query}\". Respond only one word 'relevant' or 'irrelevant'.")

        relevance_response = self.query_groq_api(client=self.client, prompt=relevance_prompt, model=self.llm_model)

        return relevance_response == "relevant"

    def generate_answer(self, query):
        """Generate an answer using RAG and the Groq API."""
        if not self.is_query_relevant(query):
            return json.dumps({"default" : PromptMessage.Default_Message})

        # retrieve from Amazon store
        results = self.retrievers["amazon"].invoke(query)

        context = " ".join([doc.page_content for doc in results])
        prompt = self.template.invoke({"context": context, "query": query}).to_string()

        answer = self.query_groq_api(client=self.client, prompt=prompt, model=self.llm_model)

        return answer

    def generate_answer_with_agent(self, query):
        """Generate an answer using agent."""
        if not self.is_query_relevant(query):
            return json.dumps({"default" : PromptMessage.Default_Message})

        with SqliteSaver.from_conn_string(":memory:") as memory:
            agent = SearchAgent(llm_model=self.llm_model,
                                embedding_model=self.embedding_model,
                                tools=self.tools,
                                client=self.client,
                                checkpointer=memory)

            logger.info(f"Thread ID: {self.thread_id}")
            thread = {"configurable": {"thread_id": self.thread_id}}
            response = agent.graph.invoke({"user_query": query},thread)

            return json.dumps(response['result'])

    def initialize_service(self):
        logger.info("Initialize the service")

        load_dotenv(find_dotenv())

        self.template = ChatPromptTemplate.from_messages(
            [PromptMessage.System_Message, PromptMessage.Human_Message, PromptMessage.AI_Message])

        # groq API client
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # model
        file_path = '../model.yaml'
        model_list = Util.load_yaml(file_path)

        self.llm_model = model_list["LLM"]
        self.embedding_model = model_list["EMBEDDING"]

        # tool
        username = os.getenv("MONGO_USER_NAME")
        password = os.getenv("MONGO_PASSWORD")
        cluster = os.getenv("MONGO_CLUSTER")
        database = os.getenv("MONGO_DATABASE")

        tavily_api_key = os.getenv("TAVILY_API_KEY")
        cohere_api_key = os.getenv("CO_API_KEY")

        co = cohere.Client(api_key=cohere_api_key)

        def embedding_function(texts, type):
            return co.embed(
                model='embed-english-v3.0',
                texts=texts,
                input_type=type
            ).embeddings

        def ranking_function(query, documents, top_n):
            response = co.rerank(model='rerank-english-v3.0', query=query,
                                 documents=[doc['content'] for doc in documents], top_n=top_n)

            return [
                documents[result.index] | {'score': result.relevance_score}
                for result in response.results
            ]

        encoded_username = quote_plus(username)
        encoded_password = quote_plus(password)

        uri = f"mongodb+srv://{encoded_username}:{encoded_password}@{cluster}.0kooc.mongodb.net/?retryWrites=true&w=majority&appName={cluster}"

        db = MongoClient(uri)[database]

        tavily_search = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        tavily_hybrid_search = TavilyHybridClient(
            api_key=tavily_api_key,
            db_provider="mongodb",
            collection=db.get_collection("embedded_picksmart"),
            index="pick_smart_vector_index",
            embeddings_field="product_title_embedding",
            content_field="product_title",
            embedding_function=embedding_function,
            ranking_function=ranking_function
        )

        self.tools = {"search": tavily_search,"hybrid_search":tavily_hybrid_search}

        # vector index
        VectorStoreService().create_vector_index(uri, db)

        # vector store
        urls = [WebURLs.Amazon, WebURLs.Ebay]
        self.retrievers = VectorStoreService(embedding_model=self.embedding_model).load_vector_store(urls=urls)