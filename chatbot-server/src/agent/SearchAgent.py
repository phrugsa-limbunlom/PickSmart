import json
import logging
from typing import Dict, List, Any, Optional

import requests
from data.SearchAgentState import SearchAgentState
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph
from constants.PromptMessage import PromptMessage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


logger = logging.getLogger(__name__)

class SearchAgent:
    """
    A search agent that processes queries and finds relevant product information.

    This agent uses a state graph to analyze queries, search online shops,
    analyze and rank results, and find product sources.

    Attributes:
        model: The language model identifier
        tools: Dictionary of search tools
        client: API client for LLM interactions
        graph: Compiled state graph for processing
    """

    def __init__(self,
                 llm_model: str,
                 tools: Dict[str, Any],
                 client: Any,
                 checkpointer: Optional[Any] = None) -> None:
        self.model = llm_model
        self.tools = tools
        self.client = client
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
        Call the LLM client with a prompt and return the response.

        Args:
            prompt: The prompt text to send to the LLM

        Returns:
            The text response from the LLM

        Raises:
            ValueError: If prompt is not a string
            requests.exceptions.HTTPError: If API request fails
        """
        try:
            if not isinstance(prompt, str):
                raise ValueError(f"Prompt must be a string, but got {type(prompt)}")

            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
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

    def analyze_query_node(self, state: SearchAgentState) -> Dict[str, List[str]]:
        """
        Analyze the user query and break it down into specific search queries.

        Args:
            state: Current state containing the user query

        Returns:
            Dictionary containing list of revised queries
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

    def search_online_node(self, state: SearchAgentState) -> Dict[str, str]:
        """
        Search for products using the revised queries.

        Args:
            state: Current state containing revised queries

        Returns:
            Dictionary containing concatenated product information
        """
        products = []

        for query in state['revised_query']:

            query = f"find the specific product title from this product requirement: {query}"

            response = self.tools["hybrid_search"].search(query=query, max_local=3, max_foreign=2, save_foreign=True)

            for r in response:
                products.append(r['content'])

        products = " ".join([product for product in products])

        return {"relevant_products": products}

    def analyze_rank_node(self, state: SearchAgentState) -> Dict[str, str]:
        """
        Analyze and rank the found products based on user requirements.

        Args:
            state: Current state containing products and user query

        Returns:
            Dictionary containing analysis results
        """
        prompt = ChatPromptTemplate.from_messages([
            PromptMessage.ANALYZE_RANK_PROMPT,
            PromptMessage.ANALYZE_RANK_HUMAN_PROMPT
        ]).invoke({"products": state["relevant_products"], "requirements": state["user_query"]}).to_string()

        return {"analyze_result": self.call_client(prompt)}

    def search_source_node(self, state: SearchAgentState) -> Dict[str, Any]:
        """
        Find product sources and additional information.

        Args:
            state: Current state containing analyzed products

        Returns:
            Dictionary containing complete product information with URLs and images
        """
        analyze_result = state["analyze_result"]

        analyze_result = json.loads(analyze_result)

        product_tiles = [product["title"] for product in analyze_result["products"]]

        query = "find the url source from e-commerce website for purchasing products only based on this product title {}"

        search_result = list(
            map(lambda title: self.tools["search"].search(query=query.format(title), max_results=1, include_images=True),
                product_tiles))

        product_images = [search["images"][0] or "" for search in search_result]

        product_urls = [search["results"][0]["url"] or "" for search in search_result]

        for idx, product in enumerate(analyze_result["products"]):
            product["image"] = product_images[idx]
            product["url"] = product_urls[idx]
        return {"result": analyze_result}