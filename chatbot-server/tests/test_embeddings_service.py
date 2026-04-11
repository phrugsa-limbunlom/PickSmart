import pytest

from src.services.embeddings import EmbeddingsService


class FakeCohereClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def embed(self, model: str, texts, input_type: str):
        class Result:
            embeddings = [[0.1, 0.2, 0.3]]
        return Result()


def test_mock_embeddings_is_deterministic() -> None:
    service = EmbeddingsService(provider_type="mock")

    vec1 = service.embed_text("hello")
    vec2 = service.embed_text("hello")

    assert vec1 == vec2
    assert len(vec1) == 1536


def test_cohere_embeddings(monkeypatch) -> None:
    monkeypatch.setattr("src.services.embeddings.cohere.Client", FakeCohereClient)
    service = EmbeddingsService(provider_type="cohere", api_key="key")

    vec = service.embed_text("hello")

    assert vec == [0.1, 0.2, 0.3]


def test_unknown_provider_raises() -> None:
    service = EmbeddingsService(provider_type="unknown")

    with pytest.raises(ValueError):
        service.embed_text("hello")
