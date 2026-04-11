"""
Vector store interfaces.

Defines abstract contracts for vector store services and persistence.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class VectorStoreInterface(ABC):
    """
    Interface for vector store database operations.
    
    Abstracts vector database operations like index creation and search,
    enabling different storage backends without changing dependent code.
    """
    
    @abstractmethod
    def create_vector_index(self) -> None:
        """
        Create a vector search index in the database if it doesn't exist.
        
        Sets up appropriate indexes for efficient vector similarity search
        with configured dimensions and similarity metrics.
        
        Returns:
            None
        """
        pass


class IVectorStoreService(ABC):
    """
    Interface for vector store service implementations.
    
    Defines contract for semantic search and vector operations.
    """
    
    @abstractmethod
    def search_similar(self, 
                      query: str, 
                      top_k: int = 5,
                      department: Optional[str] = None,
                      region: Optional[str] = None) -> List[Dict]:
        """
        Search for semantically similar products.
        
        Args:
            query: Search query
            top_k: Number of results to return
            department: Filter by department
            region: Filter by region
            
        Returns:
            List of similar products with scores
        """
        pass
    
    @abstractmethod
    def insert_vector(self, doc_id: str, text: str, metadata: Dict) -> str:
        """
        Insert a document with vector embedding.
        
        Args:
            doc_id: Document identifier
            text: Document text to embed
            metadata: Additional metadata
            
        Returns:
            Chunk ID of inserted document
        """
        pass
    
    @abstractmethod
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            True if successful
        """
        pass
