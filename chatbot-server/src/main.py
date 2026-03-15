import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any, Dict

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from service.chatbot_service import ChatbotService
from data.ChatMessage import ChatMessage

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    An asynchronous context manager that initializes and cleans up the
    Kafka producer, Kafka consumer, and ChatbotService for the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Control is yielded to allow the application to run within this context.

    Raises:
        Exception: Propagates any exceptions occurred during initialization or cleanup.
    """
    try:
        logger.info("Initializing Chatbot Service...")
        service = ChatbotService()
        service.initialize_service()
        app.state.service = service
        logger.info("Chatbot Service initialized successfully.")

        yield

    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        raise

app = FastAPI(lifespan=lifespan)

# enable cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://74.220.51.0/24"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.post("/api/chat/stream")
async def stream_chat(chat_message: ChatMessage, request: Request):
    service: ChatbotService = request.app.state.service

    async def event_generator():
        try:
            async for chunk in service.stream_answer(chat_message.message):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Error during streaming: {e}")
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")