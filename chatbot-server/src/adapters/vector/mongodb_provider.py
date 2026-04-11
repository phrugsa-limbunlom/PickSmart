"""
MongoDB Atlas vector database provider implementation.

Provides integration with MongoDB Atlas for vector search on product embeddings.
"""
import os

import certifi
from pymongo import MongoClient
from pymongo.database import Database
from urllib.parse import quote_plus


class MongoDBVectorProvider:
    """
    MongoDB Atlas vector database provider for product embeddings.
    
    Manages connections to MongoDB Atlas with support for vector search
    and SSL/TLS security for production use.
    """
    
    def __init__(self, username: str, password: str, cluster: str, database: str) -> None:
        """
        Initialize MongoDB provider with connection credentials.
        
        Args:
            username: MongoDB Atlas username
            password: MongoDB Atlas password
            cluster: MongoDB Atlas cluster name/domain
            database: Database name to connect to
        """
        encoded_username = quote_plus(username)
        encoded_password = quote_plus(password)
        self._database = database
        self._uri = (
            f"mongodb+srv://{encoded_username}:{encoded_password}@{cluster}.mongodb.net/"
            f"{database}?appName=picksmart-cluster&retryWrites=true&w=majority"
        )

    def _create_client(self) -> MongoClient:
        """
        Create a MongoDB client with proper TLS/SSL configuration.
        
        Returns:
            Configured MongoClient instance
        """
        tls_ca_file = os.getenv("MONGO_TLS_CA_FILE", certifi.where())
        os.environ.setdefault("SSL_CERT_FILE", tls_ca_file)

        return MongoClient(
            self._uri,
            tls=True,
            tlsCAFile=tls_ca_file,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000,
            retryWrites=True,
        )

    def get_database(self) -> Database:
        """
        Get MongoDB database instance with connection validation.
        
        Returns:
            Connected MongoDB database instance
        """
        client = self._create_client()
        client.admin.command("ping")
        return client[self._database]
