from pydantic import BaseModel

class ChatMessage(BaseModel):
    """
    A Pydantic model representing a chat message.

    Attributes:
        user (str): The user sending the message.
        message (str): The content of the user's message.
    """
    user: str
    message: str