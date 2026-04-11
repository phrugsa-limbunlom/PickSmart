"""
Base interfaces for service contracts.

Defines abstract interfaces that all service implementations must follow,
enabling loose coupling and easy testing with mock implementations.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class LLMClientInterface(ABC):
    """
    Interface for Language Model client providers.
    
    Abstracts the interaction with LLM services, allowing different
    implementations without changing dependent code.
    """
    
    @abstractmethod
    def generate(self, prompt: str, model: str) -> str:
        """
        Generate a response from a prompt using a specific model.
        
        Args:
            prompt: The prompt text to send to the model
            model: The model identifier to use for generation
            
        Returns:
            The text response from the model
            
        Raises:
            ValueError: If prompt is not a string
        """
        pass


class HybridSearchInterface(ABC):
    """
    Interface for hybrid product search providers.
    
    Handles searching for relevant products combining multiple search strategies.
    """
    
    @abstractmethod
    def search_products(self, query: str, max_local: int = 3, max_foreign: int = 2) -> List[str]:
        """
        Search and return a list of product text snippets.
        
        Args:
            query: The search query string
            max_local: Maximum number of local results to return
            max_foreign: Maximum number of foreign results to return
            
        Returns:
            List of product information strings
        """
        pass


class ProductSourceSearchInterface(ABC):
    """
    Interface for product source search providers.
    
    Resolves product information sources and related metadata like images.
    """
    
    @abstractmethod
    def find_sources(self, titles: List[str]) -> List[Dict[str, str]]:
        """
        Resolve product sources and images for product titles.
        
        Args:
            titles: List of product titles to find sources for
            
        Returns:
            List of dictionaries containing source information, images, and metadata
        """
        pass


class ModelProviderInterface(ABC):
    """
    Interface for model configuration providers.
    
    Abstracts the retrieval of model configuration from various sources.
    """
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        Return the LLM model name from configuration.
        
        Returns:
            The model name/identifier as a string
        """
        pass
