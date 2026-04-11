"""
Vector database adapter implementations.

Contains concrete implementations of vector database providers.
"""
from .mongodb_provider import MongoDBVectorProvider

__all__ = ["MongoDBVectorProvider"]
