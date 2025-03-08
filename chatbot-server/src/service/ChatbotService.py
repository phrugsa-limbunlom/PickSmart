import json
import logging
import os
import uuid
from typing import Optional, Any
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
from constants.PromptMessage import PromptMessage
from utils.file_utils import FileUtils

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class ChatbotService:
    """
    A service class that handles chatbot functionality including LLM interactions,
    relevance checking, and generating answers using agents.

    This service integrates with Groq API for LLM capabilities and supports
    vector search through MongoDB and Tavily for retrieving relevant information.

    Attributes:
        template: ChatPromptTemplate for structuring conversations
        client: API client for LLM interactions (typically Groq)
        llm_model: The language model identifier to use
        embedding_model: The embedding model identifier to use
        retrievers: Retriever components for information lookup
        tools: Dictionary of search tools available to the agent
        thread_id: Unique identifier for conversation thread
    """

    def __init__(self, template: Optional[str] = None,
                 client: Optional[str] = None,
                 llm_model: Optional[str] = None,
                 embedding_model: Optional[str] = None,
                 retrievers: Optional[str] = None,
                 tools: Optional[str] = None):

        """
        Initialize a new ChatbotService instance.

        Args:
            template: Optional prompt template for structuring conversations
            client: Optional API client for LLM interactions
            llm_model: Optional language model identifier
            embedding_model: Optional embedding model identifier
            retrievers: Optional retriever components
            tools: Optional dictionary of search tools
        """

        self.template = template
        self.client = client
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.retrievers = retrievers
        self.tools = tools
        self.thread_id = str(uuid.uuid4())

    def query_groq_api(self, client: Any, prompt: str, model: str) -> str:
        """
        Query the Groq API directly and return the text response.

        Args:
            client: The Groq API client
            prompt: The prompt text to send to the API
            model: The model identifier to use for generation

        Returns:
            The text response from the API

        Raises:
            ValueError: If prompt is not a string
            Various exceptions from the API client
        """
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

    def is_query_relevant(self, query: str) -> bool:
        """
        Check if a user query is relevant to the configured prompt template.

        Uses the LLM to evaluate relevance by asking it to classify the query.

        Args:
            query: The user query text to evaluate

        Returns:
            Boolean indicating whether the query is relevant
        """
        relevance_prompt = (
            f"This is prompt template : \"{self.template}\". Evaluate whether the following query is relevant to the prompt template: \"{query}\". Respond only one word 'relevant' or 'irrelevant'.")

        relevance_response = self.query_groq_api(client=self.client, prompt=relevance_prompt, model=self.llm_model)

        return relevance_response == "relevant"

    def generate_answer_with_agent(self, query: str) -> str:
        """
        Generate an answer to a query using the search agent.

        First checks if the query is relevant, then uses the agent to generate a response.
        If not relevant, returns a default message.

        Args:
            query: The user query to process

        Returns:
            String containing the response
        """
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
            response = agent.graph.invoke({"user_query": query}, thread)

            return json.dumps(response['result'])

    def initialize_service(self) -> None:
        """
        Initialize the chatbot service with necessary configurations and connections.

        Sets up:
        - Environment variables
        - Prompt template
        - API clients
        - Model configurations
        - MongoDB connection
        - Search tools
        - Vector index

        This method should be called after instantiating the service and before using it.
        """

        logger.info("Initialize the service")

        load_dotenv(find_dotenv())

        self.template = ChatPromptTemplate.from_messages(
            [PromptMessage.System_Message, PromptMessage.Human_Message, PromptMessage.AI_Message])

        # groq API client
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # model
        file_path = '../model.yaml'
        model_list = FileUtils.load_yaml(file_path)

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

        self.tools = {"search": tavily_search, "hybrid_search": tavily_hybrid_search}

        # vector index
        VectorStoreService(mongo_uri=uri, mongo_db=db).create_vector_index()