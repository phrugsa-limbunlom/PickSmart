"""
Database models using SQLModel for vector database.

Defines ORM/data models for persistent storage and vector operations.
"""
from typing import Optional
from pydantic import BaseModel


class VectorChunk(BaseModel):
    """
    Represents a document chunk with associated vector embedding.
    
    Used for storing and retrieving product information with semantic vectors.
    """
    chunk_id: str
    chunk_embedding: list
    doc_id: str
    product_title: str
    department: Optional[str] = None
    region: Optional[str] = None
