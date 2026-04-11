"""
Vector search API endpoints.

Provides endpoints for semantic search and vector database operations.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Request, Query
from pydantic import BaseModel

from src.interfaces import IVectorStoreService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vector", tags=["vector-search"])


class SearchQuery(BaseModel):
    """Vector search query request model."""
    query: str
    top_k: int = 5
    department: Optional[str] = None
    region: Optional[str] = None


class SearchResult(BaseModel):
    """Search result model."""
    similarityScore: float
    document: dict


def get_vector_store(request: Request) -> IVectorStoreService:
    """
    Dependency provider for IVectorStoreService.
    
    Args:
        request: FastAPI request object
        
    Returns:
        IVectorStoreService instance from app state
    """
    return request.app.state.vector_store


@router.post("/search")
async def semantic_search(
    search_query: SearchQuery,
    vector_store: IVectorStoreService = Depends(get_vector_store),
):
    """
    Perform semantic search on vector database.
    
    Args:
        search_query: Search parameters
        vector_store: Injected IVectorStoreService
        
    Returns:
        List of matching documents with similarity scores
    """
    try:
        results = vector_store.search_similar(
            query=search_query.query,
            top_k=search_query.top_k,
            department=search_query.department,
            region=search_query.region,
        )
        return {"results": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return {"error": str(e), "results": []}


@router.get("/search/simple")
async def simple_search(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(5, ge=1, le=100),
    vector_store: IVectorStoreService = Depends(get_vector_store),
):
    """
    Simple GET endpoint for semantic search.
    
    Args:
        query: Search query string
        top_k: Number of results
        vector_store: Injected IVectorStoreService
        
    Returns:
        Search results
    """
    results = vector_store.search_similar(query=query, top_k=top_k)
    return {"results": results, "count": len(results)}


@router.get("/status")
async def vector_db_status(
    vector_store: IVectorStoreService = Depends(get_vector_store),
):
    """
    Get vector database status.
    
    Returns:
        Status information
    """
    return {
        "status": "ready",
        "database": "MongoDB Atlas",
        "has_indexes": True,
    }
