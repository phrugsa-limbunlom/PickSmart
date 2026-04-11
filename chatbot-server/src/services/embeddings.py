"""
Embeddings service for generating vector representations.

Provides functionality to generate embeddings from text using various providers.
"""
import logging
from typing import List

import cohere

logger = logging.getLogger(__name__)


class EmbeddingsService:
    """
    Service for generating text embeddings.
    
    Wraps embedding providers to generate vector representations
    of text for semantic search and similarity operations.
    """
    
    def __init__(self, provider_type: str = "mock", **kwargs):
        """
        Initialize embeddings service.
        
        Args:
            provider_type: Type of provider (mock, cohere, openai, etc.)
            **kwargs: Provider-specific configuration
        """
        self.provider_type = provider_type
        self.kwargs = kwargs
        
        if provider_type == "cohere":
            self.client = cohere.Client(api_key=kwargs.get("api_key"))
        elif provider_type == "mock":
            self.client = None
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of float values representing the embedding
        """
        if self.provider_type == "mock":
            return self._mock_embed(text)
        elif self.provider_type == "cohere":
            return self._embed_cohere(text)
        else:
            raise ValueError(f"Unknown provider: {self.provider_type}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embeddings.append(self.embed_text(text))
        return embeddings
    
    def _mock_embed(self, text: str) -> List[float]:
        """
        Generate mock embedding (for testing).
        
        Args:
            text: Text to embed (deterministic based on content)
            
        Returns:
            List of mock embedding values
        """
        # Generate deterministic mock embedding based on text hash
        hash_val = hash(text) % (2 ** 32)
        import random
        random.seed(hash_val)
        return [random.random() for _ in range(1536)]
    
    def _embed_cohere(self, text: str) -> List[float]:
        """
        Generate embedding using Cohere API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector from Cohere
        """
        response = self.client.embed(
            model="embed-english-v3.0",
            texts=[text],
            input_type="search_document",
        )
        return response.embeddings[0]
