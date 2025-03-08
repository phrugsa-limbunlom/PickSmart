from pydantic import BaseModel

class ChatbotResponse(BaseModel):
    """
    A Pydantic model representing a chatbot response message.

    Attributes:
        value (str): The chatbot's response text.
        uid (str): A unique identifier for the response.
    """
    value: str
    uid: str