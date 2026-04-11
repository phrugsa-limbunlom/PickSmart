from types import SimpleNamespace

from fastapi import FastAPI

from src import main


class FakeVectorRepo:
    def __init__(self):
        self.initialized = False

    def initialize(self):
        self.initialized = True


class FakeContainer:
    def __init__(self):
        self.vector_db_repo = FakeVectorRepo()
        self.vector_store = "vector-store"

    def get_chat_service(self):
        return "chat-service"


def test_create_app_registers_routes() -> None:
    app = main.create_app()
    routes = [route.path for route in app.routes]

    assert "/api/chat" in routes
    assert "/api/vector/search" in routes


def test_lifespan_sets_app_state(monkeypatch) -> None:
    container = FakeContainer()
    monkeypatch.setattr(main, "get_dependency_container", lambda: container)

    app = FastAPI(lifespan=main.lifespan)

    async def _run():
        async with app.router.lifespan_context(app):
            assert app.state.chat_service == "chat-service"
            assert app.state.vector_store == "vector-store"
            assert container.vector_db_repo.initialized is True

    __import__("asyncio").run(_run())
