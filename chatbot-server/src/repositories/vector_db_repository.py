"""
Vector database repository for MongoDB operations.

Handles database initialization, index creation, and vector search setup.
"""
import logging
import time

from pymongo.database import Database
from pymongo.operations import SearchIndexModel

logger = logging.getLogger(__name__)


class VectorDBRepository:
    """
    Repository for vector database operations in MongoDB.
    
    Manages vector search index creation, initialization, and database schema setup
    for efficient semantic search on product embeddings.
    """
    
    def __init__(self, mongo_db: Database) -> None:
        """
        Initialize vector database repository.
        
        Args:
            mongo_db: MongoDB database instance
        """
        self.mongo_db = mongo_db
        self.collection_name = "embedded_picksmart"
        self.index_name = "pick_smart_vector_index"
    
    def initialize(self) -> None:
        """
        Initialize the vector database with indexes.
        
        Creates collection and vector search index if they don't exist.
        """
        self.create_collection()
        self.create_vector_index()
    
    def create_collection(self) -> None:
        """
        Create collection if it doesn't exist.
        
        Ensures the collection exists before creating indexes.
        """
        if self.collection_name not in self.mongo_db.list_collection_names():
            logger.info(f"Creating collection '{self.collection_name}'...")
            self.mongo_db.create_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' created successfully.")
    
    def create_vector_index(self) -> None:
        """
        Create vector search index for semantic search.
        
        Creates a vector index on product_title_embedding field configured for
        cosine similarity with 1024 dimensions and scalar quantization.
        """
        collection = self.mongo_db.get_collection(self.collection_name)
        
        # Check if index already exists
        existing_indexes = list(collection.list_search_indexes())
        if any(idx.get("name") == self.index_name for idx in existing_indexes):
            logger.info(f"Index '{self.index_name}' already exists. Skipping creation.")
            return
        
        search_index_model = SearchIndexModel(
            definition={
                "fields": [
                    {
                        "type": "vector",
                        "path": "product_title_embedding",
                        "numDimensions": 1024,
                        "similarity": "cosine",
                        "quantization": "scalar"
                    }
                ]
            },
            name=self.index_name,
            type="vectorSearch",
        )
        
        result = collection.create_search_index(model=search_index_model)
        logger.info(f"Creating search index '{result}'...")
        
        # Poll until index is ready
        logger.info("Waiting for index to be queryable. This may take up to a minute...")
        self._wait_for_index(collection, result)
        logger.info(f"Index '{result}' is ready for querying.")
    
    def _wait_for_index(self, collection, index_name: str, timeout_seconds: int = 60) -> None:
        """
        Wait for index to become queryable.
        
        Args:
            collection: MongoDB collection
            index_name: Name of the index to wait for
            timeout_seconds: Maximum time to wait
        """
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            indices = list(collection.list_search_indexes(index_name))
            if indices and indices[0].get("queryable"):
                return
            time.sleep(5)
        
        logger.warning(f"Index '{index_name}' did not become queryable within {timeout_seconds} seconds")
    
    def get_collection(self):
        """
        Get the vector database collection.
        
        Returns:
            MongoDB collection instance
        """
        return self.mongo_db.get_collection(self.collection_name)
