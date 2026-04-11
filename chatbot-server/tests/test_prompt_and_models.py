from src.services.prompt_messages import PromptMessage
from src.models.schemas import ChatMessage, ChatbotResponse
from src.models.vector_db import VectorChunk


def test_prompt_messages_have_defaults() -> None:
    assert "assistant" in PromptMessage.System_Message
    assert "Hello" in PromptMessage.Default_Message


def test_schema_models_create() -> None:
    message = ChatMessage(user="u", message="hello")
    response = ChatbotResponse(value="ok", uid="1")

    assert message.user == "u"
    assert response.uid == "1"


def test_vector_chunk_model() -> None:
    chunk = VectorChunk(
        chunk_id="c1",
        chunk_embedding=[0.1, 0.2],
        doc_id="d1",
        product_title="title",
    )

    assert chunk.department is None
