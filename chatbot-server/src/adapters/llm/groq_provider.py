"""
Groq LLM provider implementation.

Provides integration with Groq API for fast language model inference.
"""
import logging
import requests.exceptions
from groq import Groq

from src.interfaces import LLMClientInterface

logger = logging.getLogger(__name__)


class GroqProvider(LLMClientInterface):
    """
    Groq LLM provider for fast language model inference.
    
    Implementation of LLMClientInterface using Groq's API for generating
    text completions with high performance.
    """
    
    def __init__(self, api_key: str) -> None:
        """
        Initialize Groq provider with API credentials.
        
        Args:
            api_key: Groq API key for authentication
        """
        self._client = Groq(api_key=api_key)

    def generate(self, prompt: str, model: str) -> str:
        """
        Generate a response from a prompt using Groq API.
        
        Args:
            prompt: The prompt text to send to the model
            model: The model identifier to use for generation
            
        Returns:
            The text response from the model
            
        Raises:
            ValueError: If prompt is not a string
            requests.exceptions.HTTPError: If API request fails
        """
        if not isinstance(prompt, str):
            raise ValueError(f"Prompt must be a string, but got {type(prompt)}")

        try:
            response = self._client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                temperature=0.5,
                max_tokens=1024,
                stop=None,
                stream=False,
            )
            return response.choices[0].message.content
        except requests.exceptions.HTTPError as e:
            logger.error("HTTP Error occurred: %s - %s", e.response.status_code, e.response.text)
            raise
