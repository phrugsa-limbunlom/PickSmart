import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.routes import router
from src.models.schemas import ChatMessage


class FakeChatService:
    async def stream_chat(self, query: str):
        yield json.dumps({"type": "result", "data": {"value": "ok"}})


class ErrorChatService:
    async def stream_chat(self, query: str):
        if False:
            yield ""
        raise RuntimeError("boom")


def test_send_message_returns_results() -> None:
    app = FastAPI()
    app.state.chat_service = FakeChatService()
    app.include_router(router)

    client = TestClient(app)

    response = client.post("/api/chat", json={"user": "u", "message": "hi"})

    assert response.status_code == 200
    assert response.json() == {"results": [json.dumps({"type": "result", "data": {"value": "ok"}})]}


def test_stream_message_emits_events() -> None:
    app = FastAPI()
    app.state.chat_service = FakeChatService()
    app.include_router(router)

    client = TestClient(app)

    response = client.post("/api/chat/stream", json={"user": "u", "message": "hi"})

    body = response.text
    assert "data:" in body


def test_stream_message_returns_error_event() -> None:
    app = FastAPI()
    app.state.chat_service = ErrorChatService()
    app.include_router(router)

    client = TestClient(app)

    response = client.post("/api/chat/stream", json={"user": "u", "message": "hi"})

    assert "error" in response.text


def test_health_check() -> None:
    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}