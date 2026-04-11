"""
Interfaces layer - Abstract service contracts.

This layer defines abstract interfaces that other layers depend on,
following the Dependency Inversion Principle for loose coupling.
"""
from .base import (
    LLMClientInterface,
    HybridSearchInterface,
    ProductSourceSearchInterface,
    ModelProviderInterface,
)
from .vector_store import VectorStoreInterface, IVectorStoreService
from .chat import IChatService

__all__ = [
    "LLMClientInterface",
    "HybridSearchInterface",
    "ProductSourceSearchInterface",
    "ModelProviderInterface",
    "VectorStoreInterface",
    "IVectorStoreService",
    "IChatService",
]
