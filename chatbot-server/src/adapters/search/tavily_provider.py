"""
Tavily search provider implementations.

Provides integration with Tavily API for hybrid product search and web search.
"""
from typing import Dict, List

import cohere
from pymongo.database import Database
from tavily import TavilyClient, TavilyHybridClient

from src.interfaces import HybridSearchInterface, ProductSourceSearchInterface


class TavilyHybridSearchProvider(HybridSearchInterface):
    """
    Tavily hybrid search provider combining MongoDB and web search.
    
    Implements hybrid search capabilities using both local MongoDB
    vector search and Tavily's web search for comprehensive results.
    """
    
    def __init__(self, api_key: str, mongo_db: Database, cohere_api_key: str) -> None:
        """
        Initialize Tavily hybrid search provider.
        
        Args:
            api_key: Tavily API key for authentication
            mongo_db: MongoDB database instance for local search
            cohere_api_key: Cohere API key for embeddings and reranking
        """
        self._cohere = cohere.Client(api_key=cohere_api_key)

        def embedding_function(texts, input_type):
            """Generate embeddings using Cohere API."""
            return self._cohere.embed(
                model="embed-english-v3.0",
                texts=texts,
                input_type=input_type,
            ).embeddings

        def ranking_function(query, documents, top_n):
            """Rerank documents using Cohere's rerank model."""
            response = self._cohere.rerank(
                model="rerank-english-v3.0",
                query=query,
                documents=[doc["content"] for doc in documents],
                top_n=top_n,
            )
            return [
                documents[result.index] | {"score": result.relevance_score}
                for result in response.results
            ]

        self._client = TavilyHybridClient(
            api_key=api_key,
            db_provider="mongodb",
            collection=mongo_db.get_collection("embedded_picksmart"),
            index="pick_smart_vector_index",
            embeddings_field="product_title_embedding",
            content_field="product_title",
            embedding_function=embedding_function,
            ranking_function=ranking_function,
        )

    def search_products(self, query: str, max_local: int = 3, max_foreign: int = 2) -> List[str]:
        """
        Search for products using hybrid search.
        
        Args:
            query: The search query string
            max_local: Maximum number of local results to return
            max_foreign: Maximum number of foreign web results to return
            
        Returns:
            List of product information strings
        """
        response = self._client.search(
            query=query,
            max_local=max_local,
            max_foreign=max_foreign,
            save_foreign=True,
        )
        return [item.get("content", "") for item in response if item.get("content")]


class TavilySourceSearchProvider(ProductSourceSearchInterface):
    """
    Tavily web search provider for product URLs and images.
    
    Uses Tavily web search to find product sources, URLs, and images
    from e-commerce websites.
    """
    
    def __init__(self, api_key: str) -> None:
        """
        Initialize Tavily source search provider.
        
        Args:
            api_key: Tavily API key for authentication
        """
        self._client = TavilyClient(api_key=api_key)

    def find_sources(self, titles: List[str]) -> List[Dict[str, str]]:
        """
        Find product sources and images for product titles.
        
        Args:
            titles: List of product titles to find sources for
            
        Returns:
            List of dictionaries with image and url for each product
        """
        query_template = (
            "find the url source from e-commerce website for purchasing products "
            "only based on this product title {}"
        )

        results: List[Dict[str, str]] = []
        for title in titles:
            search = self._client.search(
                query=query_template.format(title),
                max_results=1,
                include_images=True,
            )

            image = ""
            url = ""

            images = search.get("images") or []
            if images:
                image = images[0] or ""

            search_results = search.get("results") or []
            if search_results:
                url = search_results[0].get("url", "") or ""

            results.append({"image": image, "url": url})

        return results
