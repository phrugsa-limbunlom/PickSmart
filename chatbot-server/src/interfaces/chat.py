"""
Chat service interface.

Defines abstract contract for chat service implementations.
"""
from abc import ABC, abstractmethod


class IChatService(ABC):
    """
    Interface for chat service implementations.
    
    Defines contract for chat handling and conversation management.
    """
    
    @abstractmethod
    def query_llm(self, prompt: str, model: str) -> str:
        """
        Query the LLM.
        
        Args:
            prompt: Prompt text
            model: Model identifier
            
        Returns:
            LLM response
        """
        pass
    
    @abstractmethod
    def is_query_relevant(self, query: str) -> bool:
        """
        Check if query is relevant to the service's domain.
        
        Args:
            query: Query to evaluate
            
        Returns:
            True if relevant
        """
        pass
    
    @abstractmethod
    async def stream_chat(self, query: str):
        """
        Stream chat response asynchronously.
        
        Args:
            query: User query
            
        Yields:
            Response chunks
        """
        pass
