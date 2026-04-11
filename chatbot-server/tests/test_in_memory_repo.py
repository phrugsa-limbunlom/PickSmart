from src.repositories.in_memory import InMemoryConversationStore
from src.models.schemas import ChatMessage


def test_in_memory_store_crud() -> None:
    store = InMemoryConversationStore()
    message = ChatMessage(user="u1", message="hello")

    store.save_conversation("c1", [message])
    assert store.get_conversation("c1") == [message]

    store.add_message("c1", ChatMessage(user="u1", message="next"))
    assert len(store.get_conversation("c1")) == 2

    assert store.delete_conversation("c1") is True
    assert store.get_conversation("c1") is None
