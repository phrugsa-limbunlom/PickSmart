"""
Chat API endpoints.

Provides RESTful endpoints for chat interactions and streaming responses.
"""
import logging
import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from src.models.schemas import ChatMessage
from src.interfaces import IChatService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


def get_chat_service(request: Request) -> IChatService:
    """
    Dependency provider for ChatService.
    
    Args:
        request: FastAPI request object
        
    Returns:
        ChatService instance from app state
    """
    return request.app.state.chat_service


@router.post("/chat")
async def send_message(
    chat_message: ChatMessage,
    service: IChatService = Depends(get_chat_service),
):
    """
    Send a chat message.
    
    Args:
        chat_message: The user's message
        service: Injected ChatService
        
    Returns:
        JSON response with chat result
    """
    results = []
    async for chunk in service.stream_chat(chat_message.message):
        results.append(chunk)
    return {"results": results}


@router.post("/chat/stream")
async def stream_message(
    chat_message: ChatMessage,
    service: IChatService = Depends(get_chat_service),
):
    """
    Stream chat response as Server-Sent Events.
    
    Args:
        chat_message: The user's message
        service: Injected ChatService
        
    Returns:
        StreamingResponse with SSE events
    """
    
    async def event_generator():
        try:
            async for chunk in service.stream_chat(chat_message.message):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logger.error(f"Error in stream_message: {e}")
            error_response = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error_response)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Status response
    """
    return {"status": "healthy"}
