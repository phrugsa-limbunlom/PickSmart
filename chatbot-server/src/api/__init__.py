"""
API layer - FastAPI route handlers.

Contains API endpoints for chat and product search interactions.
"""
from .routes import router as chat_router
from .vector_search import router as vector_router

# Main router combining all endpoints
__all__ = ["chat_router", "vector_router"]
