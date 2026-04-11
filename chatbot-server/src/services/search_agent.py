"""
Search agent implementation using LangGraph state machine.

Implements the multi-step product search and analysis pipeline.
"""
import json
import logging
from typing import Dict, List, Any, Optional

from src.interfaces import LLMClientInterface, HybridSearchInterface, ProductSourceSearchInterface
from src.models import SearchAgentState
from src.services.prompt_messages import PromptMessage
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class SearchAgent:
    """
    Product search agent using LangGraph state machine.
    
    This agent processes user queries through a multi-step pipeline:
    1. Analyze query and break into multiple search queries
    2. Search online shops and local database for products
    3. Analyze and rank results based on user requirements
    4. Find product sources and URLs

    Attributes:
        model: The language model identifier
        llm_client: LLM adapter for generating responses
        hybrid_search: Adapter for product search
        source_search: Adapter for finding product sources
        graph: Compiled LangGraph state graph
    """

    def __init__(self,
                 llm_model: str,
                 llm_client: LLMClientInterface,
                 hybrid_search: HybridSearchInterface,
                 source_search: ProductSourceSearchInterface,
                 checkpointer: Optional[Any] = None) -> None:
        """
        Initialize the search agent.

        Args:
            llm_model: Language model identifier to use
            llm_client: LLM adapter for inference
            hybrid_search: Hybrid search adapter for products
            source_search: Search adapter for product sources
            checkpointer: Optional checkpoint saver for state persistence
        """
        self.model = llm_model
        self.llm_client = llm_client
        self.hybrid_search = hybrid_search
        self.source_search = source_search
        
        graph = StateGraph(SearchAgentState)
        graph.add_node("analyze_query", self.analyze_query_node)
        graph.add_node("search_online_shop", self.search_online_node)
        graph.add_node("analyze_and_rank", self.analyze_rank_node)
        graph.add_node("search_product_source", self.search_source_node)
        graph.set_entry_point("analyze_query")
        graph.add_edge("analyze_query", "search_online_shop")
        graph.add_edge("search_online_shop", "analyze_and_rank")
        graph.add_edge("analyze_and_rank", "search_product_source")
        graph.set_finish_point("analyze_and_rank")
        self.graph = graph.compile(checkpointer=checkpointer)

    def call_client(self, prompt: str) -> str:
        """
        Call the LLM client with a prompt.

        Args:
            prompt: The prompt text to send to the LLM

        Returns:
            The text response from the LLM

        Raises:
            ValueError: If prompt is not a string
        """
        try:
            if not isinstance(prompt, str):
                raise ValueError(f"Prompt must be a string, but got {type(prompt)}")
            return self.llm_client.generate(prompt=prompt, model=self.model)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            raise

    def analyze_query_node(self, state: SearchAgentState) -> Dict[str, List[str]]:
        """
        Analyze user query and generate multiple search queries.

        Takes the user's input query and uses the LLM to break it down
        into multiple effective search queries for product discovery.

        Args:
            state: Current agent state containing user query

        Returns:
            Dictionary with revised_query field containing list of search queries
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=PromptMessage.ANALYZE_QUERY_PROMPT),
                HumanMessage(content=state['user_query'])
            ]
        )

        response = self.call_client(prompt.invoke({}).to_string())

        queries = []
        for query in response.split("|"):
            queries.append(query)

        return {"revised_query": queries}

    async def search_online_node(self, state: SearchAgentState) -> Dict[str, str]:
        """
        Search for products using revised queries.

        Executes hybrid search across local database and web for each
        revised query, aggregating relevant product information.

        Args:
            state: Current agent state containing revised queries

        Returns:
            Dictionary with relevant_products field containing concatenated products
        """
        products = []

        for query in state['revised_query']:

            query = f"find the specific product title from this product requirement: {query}"
            response = await asyncio.to_thread(
                self.hybrid_search.search_products,
                query,
                3,
                2,
            )
            products.extend(response)

        products = " ".join([product for product in products])

        return {"relevant_products": products}

    def analyze_rank_node(self, state: SearchAgentState) -> Dict[str, str]:
        """
        Analyze and rank products based on user requirements.

        Uses the LLM to evaluate and rank found products according
        to the original user requirements.

        Args:
            state: Current agent state with products and user query

        Returns:
            Dictionary with analyze_result field containing ranked products
        """
        prompt = ChatPromptTemplate.from_messages([
            PromptMessage.ANALYZE_RANK_PROMPT,
            PromptMessage.ANALYZE_RANK_HUMAN_PROMPT
        ]).invoke({"products": state["relevant_products"], "requirements": state["user_query"]}).to_string()

        return {"analyze_result": self.call_client(prompt)}

    def search_source_node(self, state: SearchAgentState) -> Dict[str, Any]:
        """
        Find product sources, URLs, and images.

        Resolves product metadata including purchase URLs and product images
        from e-commerce websites for the top-ranked products.

        Args:
            state: Current agent state with analyzed products

        Returns:
            Dictionary with result field containing complete product information
        """
        analyze_result = state["analyze_result"]

        analyze_result = json.loads(analyze_result)

        product_titles = [product["title"] for product in analyze_result["products"]]
        product_sources = self.source_search.find_sources(product_titles)

        for idx, product in enumerate(analyze_result["products"]):
            product["image"] = product_sources[idx].get("image", "")
            product["url"] = product_sources[idx].get("url", "")
        return {"result": analyze_result}
