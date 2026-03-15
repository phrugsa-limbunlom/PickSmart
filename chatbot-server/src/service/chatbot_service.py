import json
import logging
import os
import uuid
from typing import Optional, Any
from urllib.parse import quote_plus

import cohere
import certifi
import requests.exceptions
from agent.SearchAgent import SearchAgent
from dotenv import load_dotenv, find_dotenv
from groq import Groq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from service.vector_store import VectorStoreService
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
        retrievers: Retriever components for information lookup
        tools: Dictionary of search tools available to the agent
        thread_id: Unique identifier for conversation thread
    """

    def __init__(self, template: Optional[str] = None,
                 client: Optional[str] = None,
                 llm_model: Optional[str] = None,
                 retrievers: Optional[str] = None,
                 tools: Optional[str] = None):

        """
        Initialize a new ChatbotService instance.

        Args:
            template: Optional prompt template for structuring conversations
            client: Optional API client for LLM interactions
            llm_model: Optional language model identifier
            retrievers: Optional retriever components
            tools: Optional dictionary of search tools
        """

        self.template = template
        self.client = client
        self.llm_model = llm_model
        self.retrievers = retrievers
        self.tools = tools
        self.thread_id = str(uuid.uuid4())

    def _create_mongo_client(self, uri: str) -> MongoClient:
        """
        Build a TLS-enabled MongoDB client with explicit CA bundle and
        relaxed OpenSSL security level for Atlas compatibility.
        """
        tls_ca_file = os.getenv("MONGO_TLS_CA_FILE", certifi.where())

        # Ensure system-wide SSL picks up certifi CA bundle
        os.environ.setdefault("SSL_CERT_FILE", tls_ca_file)

        return MongoClient(
            uri,
            tls=True,
            tlsCAFile=tls_ca_file,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000,
            retryWrites=True,
        )

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

    async def stream_answer(self, query: str):
        """
        Stream progress events and the final result for a query.

        Yields JSON-encoded SSE events of two types:
        - {"type": "progress", "message": "..."}  — sent as each graph node starts
        - {"type": "result", "data": {...}}         — sent once the final result is ready

        Args:
            query: The user query to process
        """
        if not self.is_query_relevant(query):
            yield json.dumps({"type": "result", "data": {"default": PromptMessage.Default_Message}})
            return

        NODE_MESSAGES = {
            "analyze_query": "Understanding your request...",
            "search_online_shop": "Searching for products...",
            "analyze_and_rank": "Ranking and analyzing results...",
            "search_product_source": "Finding product sources...",
        }

        async with AsyncSqliteSaver.from_conn_string(":memory:") as memory:
            agent = SearchAgent(llm_model=self.llm_model,
                                tools=self.tools,
                                client=self.client,
                                checkpointer=memory)

            logger.info(f"Thread ID: {self.thread_id}")
            thread = {"configurable": {"thread_id": self.thread_id}}

            async for chunk in agent.graph.astream({"user_query": query}, thread, stream_mode="updates"):
                node_name = next(iter(chunk))
                state_update = chunk[node_name]

                if node_name in NODE_MESSAGES:
                    yield json.dumps({"type": "progress", "message": NODE_MESSAGES[node_name]})

                if "result" in state_update:
                    yield json.dumps({"type": "result", "data": state_update["result"]})
    

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


        uri = f"mongodb+srv://{encoded_username}:{encoded_password}@{cluster}.mongodb.net/{database}?appName=picksmart-cluster&retryWrites=true&w=majority"

        mongo_client = self._create_mongo_client(uri)
        try:
            mongo_client.admin.command("ping")
        except PyMongoError as e:
            logger.exception("MongoDB connection failed during startup")
            raise RuntimeError(
                "Failed to connect to MongoDB Atlas. Verify database network access, "
                "credentials, cluster name, and TLS settings."
            ) from e

        db = mongo_client[database]

        tavily_search = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        # vector index
        VectorStoreService(mongo_db=db).create_vector_index()

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