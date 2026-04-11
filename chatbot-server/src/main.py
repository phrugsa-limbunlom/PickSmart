"""
FastAPI application factory and entry point.

Sets up the FastAPI application with middleware, health checks,
and dependency initialization for production readiness.
"""
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import PyMongoError

from src.api.routes import router as chat_router
from src.api.vector_search import router as vector_router
from src.config import get_dependency_container

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan context manager for startup and shutdown.
    
    Handles application initialization including:
    - Loading environment variables
    - Initializing dependency container
    - Setting up vector database indexes
    - Cleaning up resources on shutdown

    Args:
        app: FastAPI application instance

    Yields:
        None, allowing the application to run within this context

    Raises:
        PyMongoError: If database connection fails
    """
    try:
        load_dotenv(find_dotenv())
        logger.info("Initializing Chatbot Application...")

        # Get dependency container and initialize services
        container = get_dependency_container()
        
        # Initialize vector database
        logger.info("Setting up vector database...")
        container.vector_db_repo.initialize()
        
        # Create and store services in app state
        chat_service = container.get_chat_service()
        vector_store = container.vector_store
        
        app.state.chat_service = chat_service
        app.state.vector_store = vector_store
        
        logger.info("Application initialized successfully")
        
    except PyMongoError as e:
        logger.error(f"MongoDB Error: {e}")
        raise
    except Exception as e:
        logger.error(f"Initialization Error: {e}")
        raise

    # Application runs here
    yield

    # Cleanup on shutdown
    logger.info("Cleaning up resources...")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Sets up:
    - CORS middleware
    - Route handlers
    - Lifespan context manager
    - Error handling

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="PickSmart Chatbot API",
        description="Product recommendation chatbot with semantic search",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Configure CORS
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routers
    app.include_router(chat_router)
    app.include_router(vector_router)

    return app


# Create application instance for production
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
