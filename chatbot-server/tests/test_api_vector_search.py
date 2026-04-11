from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.vector_search import router


class FakeVectorStore:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def search_similar(self, query: str, top_k: int = 5, department=None, region=None):
        self.calls.append((query, top_k, department, region))
        return self.results


class ErrorVectorStore:
    def search_similar(self, query: str, top_k: int = 5, department=None, region=None):
        raise RuntimeError("boom")


def test_semantic_search_returns_results() -> None:
    app = FastAPI()
    app.state.vector_store = FakeVectorStore([{"id": 1}])
    app.include_router(router)

    client = TestClient(app)

    response = client.post("/api/vector/search", json={"query": "shoes", "top_k": 2})

    assert response.status_code == 200
    assert response.json() == {"results": [{"id": 1}], "count": 1}


def test_simple_search_get() -> None:
    app = FastAPI()
    app.state.vector_store = FakeVectorStore([{"id": 1}])
    app.include_router(router)

    client = TestClient(app)

    response = client.get("/api/vector/search/simple", params={"query": "shoes", "top_k": 1})

    assert response.status_code == 200
    assert response.json() == {"results": [{"id": 1}], "count": 1}


def test_vector_db_status() -> None:
    app = FastAPI()
    app.state.vector_store = FakeVectorStore([])
    app.include_router(router)

    client = TestClient(app)

    response = client.get("/api/vector/status")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_semantic_search_handles_error() -> None:
    app = FastAPI()
    app.state.vector_store = ErrorVectorStore()
    app.include_router(router)

    client = TestClient(app)

    response = client.post("/api/vector/search", json={"query": "shoes"})

    assert response.status_code == 200
    assert response.json()["results"] == []
