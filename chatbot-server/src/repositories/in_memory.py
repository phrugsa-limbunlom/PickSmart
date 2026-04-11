"""
In-memory conversation store repository.

Provides temporary storage for conversation history without persistence.
Useful for stateless API servers and testing.
"""
from typing import Dict, List, Optional
from src.models import ChatMessage


class InMemoryConversationStore:
    """
    In-memory store for conversation history.
    
    Stores conversations in memory without database persistence.
    Suitable for development, testing, and stateless deployments.
    """
    
    def __init__(self):
        """Initialize empty conversation store."""
        self._conversations: Dict[str, List[ChatMessage]] = {}
    
    def save_conversation(self, conversation_id: str, messages: List[ChatMessage]) -> None:
        """
        Save conversation messages to memory.
        
        Args:
            conversation_id: Unique identifier for conversation
            messages: List of chat messages to store
        """
        self._conversations[conversation_id] = messages
    
    def get_conversation(self, conversation_id: str) -> Optional[List[ChatMessage]]:
        """
        Retrieve conversation by ID.
        
        Args:
            conversation_id: Unique identifier for conversation
            
        Returns:
            List of chat messages or None if not found
        """
        return self._conversations.get(conversation_id)
    
    def add_message(self, conversation_id: str, message: ChatMessage) -> None:
        """
        Add a single message to conversation.
        
        Args:
            conversation_id: Unique identifier for conversation
            message: Message to add
        """
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []
        self._conversations[conversation_id].append(message)
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete conversation from store.
        
        Args:
            conversation_id: Unique identifier for conversation
            
        Returns:
            True if deleted, False if not found
        """
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            return True
        return False
