"""
API request/response schemas using Pydantic.

Defines the contract for API endpoints with validation and documentation.
"""
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """
    Request model for chat messages.
    
    Attributes:
        user: The user identifier sending the message
        message: The content of the user's message
    """
    user: str
    message: str


class ChatbotResponse(BaseModel):
    """
    Response model for chatbot replies.
    
    Attributes:
        value: The chatbot's response text
        uid: Unique identifier for the response
    """
    value: str
    uid: str
