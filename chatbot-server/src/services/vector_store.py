"""
Vector store service for semantic search operations.

Provides high-level interface for searching and storing vectors.
"""
import logging
from typing import List, Dict, Optional

from src.interfaces import IVectorStoreService
from src.repositories.vector_db_repository import VectorDBRepository
from src.services.embeddings import EmbeddingsService

logger = logging.getLogger(__name__)


class VectorStoreService(IVectorStoreService):
    """
    Service for vector search and storage operations.
    
    Combines embeddings generation with vector search to enable
    semantic similarity search on product data.
    
    Implements IVectorStoreService contract for dependency injection.
    """
    
    def __init__(self, 
                 vector_db_repo: VectorDBRepository,
                 embeddings_service: EmbeddingsService):
        """
        Initialize vector store service.
        
        Args:
            vector_db_repo: Vector database repository
            embeddings_service: Embeddings generation service
        """
        self.repo = vector_db_repo
        self.embeddings = embeddings_service
    
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
            List of similar documents with scores
        """
        # Generate embedding for query
        query_embedding = self.embeddings.embed_text(query)
        
        # Build search query pipeline
        collection = self.repo.get_collection()
        
        pipeline = [
            {
                "$search": {
                    "cosmosSearch": {
                        "vector": query_embedding,
                        "k": top_k,
                    },
                    "returnBase64EncodedVectors": False,
                }
            },
            {
                "$project": {
                    "similarityScore": {"$meta": "searchScore"},
                    "document": "$$ROOT",
                }
            },
        ]
        
        # Add filters if provided
        if department or region:
            match_stage = {}
            if department:
                match_stage["department"] = department
            if region:
                match_stage["region"] = region
            pipeline.append({"$match": match_stage})
        
        try:
            results = list(collection.aggregate(pipeline))
            logger.info(f"Found {len(results)} similar items for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return []
    
    def insert_vector(self, vector_data: Dict) -> str:
        """
        Insert a vector document into the store.
        
        Args:
            vector_data: Document with vector embedding
            
        Returns:
            Document ID
        """
        collection = self.repo.get_collection()
        result = collection.insert_one(vector_data)
        logger.info(f"Inserted vector document: {result.inserted_id}")
        return str(result.inserted_id)
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete document from vector store.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            True if deleted, False if not found
        """
        from bson import ObjectId
        collection = self.repo.get_collection()
        result = collection.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0
