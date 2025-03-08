import logging
import time

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.operations import SearchIndexModel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class VectorStoreService:

    def __init__(self, mongo_uri: str, mongo_db: Database) -> None:
        """
        Initialize the VectorStoreService.

        Args:
            mongo_uri: MongoDB connection URI string
            mongo_db: MongoDB database instance to work with
        """
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    def create_vector_index(self) -> MongoClient:
        """
        Create a vector search index in the MongoDB collection if it doesn't exist.

        Creates a vector search index named 'pick_smart_vector_index' in the
        'embedded_picksmart' collection, configured for cosine similarity on
        product_title_embedding vectors with 1024 dimensions.

        Returns:
            MongoClient: The MongoDB client instance (closed after operation)
        """

        client = MongoClient(self.mongo_uri)

        collection_name = "embedded_picksmart"
        collection = self.mongo_db.get_collection(collection_name)

        collection_list = self.mongo_db.list_collection_names()

        for collection in collection_list:
            if collection == collection_name:
                logger.info(f"Collection '{collection}' already exists. Skip creating vector index.")
                client.close()
            return client

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
            name="pick_smart_vector_index",
            type="vectorSearch",
        )
        result = collection.create_search_index(model=search_index_model)
        logger.info("New search index named " + result + " is building.")

        # Wait for initial sync to complete
        logger.info("Polling to check if the index is ready. This may take up to a minute.")

        predicate = None
        if predicate is None:
            predicate = lambda index: index.get("queryable") is True
        while True:
            indices = list(collection.list_search_indexes(result))
            if len(indices) and predicate(indices[0]):
                break
            time.sleep(5)

        logger.info(result + " is ready for querying.")

        client.close()

        return client