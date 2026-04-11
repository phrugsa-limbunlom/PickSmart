import json
from types import SimpleNamespace

import pytest

from src.services.chat import ChatService
from src.services.prompt_messages import PromptMessage


class FakeLLMClient:
    def __init__(self, response: str):
        self.response = response
        self.calls = []

    def generate(self, prompt: str, model: str) -> str:
        self.calls.append((prompt, model))
        return self.response


class FakeHybridSearch:
    def search_products(self, query: str, max_local: int = 3, max_foreign: int = 2):
        return []


class FakeSourceSearch:
    def find_sources(self, titles):
        return []


class FakeGraph:
    def __init__(self, updates):
        self._updates = updates

    async def astream(self, payload, thread, stream_mode="updates"):
        for update in self._updates:
            yield update


class FakeSearchAgent:
    def __init__(self, **kwargs):
        self.graph = FakeGraph(kwargs["updates"])


def collect_async(async_iter):
    async def _collect():
        items = []
        async for item in async_iter:
            items.append(item)
        return items

    return __import__("asyncio").run(_collect())


def test_query_llm_requires_string() -> None:
    service = ChatService(llm_client=FakeLLMClient("ok"), llm_model="m")

    with pytest.raises(ValueError):
        service.query_llm(prompt=123, model="m")


def test_is_query_relevant_checks_response() -> None:
    llm = FakeLLMClient("relevant")
    service = ChatService(llm_client=llm, llm_model="m")

    assert service.is_query_relevant("find shoes") is True


def test_stream_chat_returns_default_for_irrelevant(monkeypatch) -> None:
    llm = FakeLLMClient("irrelevant")
    service = ChatService(llm_client=llm, llm_model="m")

    results = collect_async(service.stream_chat("query"))

    assert results == [json.dumps({"type": "result", "data": {"default": PromptMessage.Default_Message}})]


def test_stream_chat_emits_progress_and_result(monkeypatch) -> None:
    llm = FakeLLMClient("relevant")
    service = ChatService(llm_client=llm, llm_model="m")

    updates = [
        {"analyze_query": {}},
        {"search_online_shop": {}},
        {"analyze_and_rank": {"result": {"final": {"message": "done"}}}},
    ]

    monkeypatch.setattr("src.services.chat.SearchAgent", lambda **kwargs: FakeSearchAgent(updates=updates))

    results = collect_async(service.stream_chat("query"))

    assert json.loads(results[-1])["type"] == "result"
    assert json.loads(results[-1])["data"]["final"]["message"] == "done"
