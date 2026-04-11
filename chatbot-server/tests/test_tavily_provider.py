from typing import List

from src.adapters.search.tavily_provider import (
    TavilyHybridSearchProvider,
    TavilySourceSearchProvider,
)


class FakeCollection:
    def __init__(self):
        self.name = "embedded_picksmart"


class FakeMongoDB:
    def get_collection(self, name: str):
        return FakeCollection()


class FakeCohereClient:
    def embed(self, model: str, texts: List[str], input_type: str):
        class Result:
            embeddings = [[0.1, 0.2]]
        return Result()

    def rerank(self, model: str, query: str, documents: List[str], top_n: int):
        class RerankResult:
            def __init__(self, index: int, score: float):
                self.index = index
                self.relevance_score = score

        class Response:
            results = [RerankResult(0, 0.9)]

        return Response()


class FakeTavilyHybridClient:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self._results = []

    def search(self, **kwargs):
        return self._results


class FakeTavilyClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._search = {}

    def search(self, **kwargs):
        return self._search


def test_tavily_hybrid_search_filters_empty_content(monkeypatch) -> None:
    monkeypatch.setattr("src.adapters.search.tavily_provider.cohere.Client", lambda api_key: FakeCohereClient())
    monkeypatch.setattr("src.adapters.search.tavily_provider.TavilyHybridClient", lambda **kwargs: FakeTavilyHybridClient(**kwargs))

    provider = TavilyHybridSearchProvider(
        api_key="key",
        mongo_db=FakeMongoDB(),
        cohere_api_key="cohere",
    )

    provider._client._results = [
        {"content": "item-1"},
        {"missing": "skip"},
        {"content": "item-2"},
    ]

    result = provider.search_products("query")

    assert result == ["item-1", "item-2"]


def test_tavily_source_search_returns_image_and_url(monkeypatch) -> None:
    fake_client = FakeTavilyClient(api_key="key")
    fake_client._search = {
        "images": ["img-1"],
        "results": [{"url": "https://example.com"}],
    }
    monkeypatch.setattr("src.adapters.search.tavily_provider.TavilyClient", lambda api_key: fake_client)

    provider = TavilySourceSearchProvider(api_key="key")

    result = provider.find_sources(["title"])

    assert result == [{"image": "img-1", "url": "https://example.com"}]
