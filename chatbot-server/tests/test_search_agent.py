import json

from src.services.search_agent import SearchAgent


class FakeLLMClient:
    def __init__(self, response: str):
        self.response = response

    def generate(self, prompt: str, model: str) -> str:
        return self.response


class FakeHybridSearch:
    def __init__(self, results):
        self.results = results
        self.queries = []

    def search_products(self, query: str, max_local: int = 3, max_foreign: int = 2):
        self.queries.append(query)
        return self.results


class FakeSourceSearch:
    def __init__(self, sources):
        self.sources = sources
        self.titles = []

    def find_sources(self, titles):
        self.titles = titles
        return self.sources


def test_analyze_query_node_splits_response() -> None:
    agent = SearchAgent(
        llm_model="model",
        llm_client=FakeLLMClient("q1|q2"),
        hybrid_search=FakeHybridSearch([]),
        source_search=FakeSourceSearch([]),
    )

    result = agent.analyze_query_node({"user_query": "find"})

    assert result["revised_query"] == ["q1", "q2"]


def test_search_online_node_aggregates_results() -> None:
    agent = SearchAgent(
        llm_model="model",
        llm_client=FakeLLMClient("q1"),
        hybrid_search=FakeHybridSearch(["p1", "p2"]),
        source_search=FakeSourceSearch([]),
    )

    result = __import__("asyncio").run(agent.search_online_node({"revised_query": ["a", "b"]}))

    assert result["relevant_products"] == "p1 p2 p1 p2"


def test_analyze_rank_node_uses_llm() -> None:
    agent = SearchAgent(
        llm_model="model",
        llm_client=FakeLLMClient("ranked"),
        hybrid_search=FakeHybridSearch([]),
        source_search=FakeSourceSearch([]),
    )

    result = agent.analyze_rank_node({"relevant_products": "p1", "user_query": "need"})

    assert result == {"analyze_result": "ranked"}


def test_search_source_node_adds_sources() -> None:
    agent = SearchAgent(
        llm_model="model",
        llm_client=FakeLLMClient(""),
        hybrid_search=FakeHybridSearch([]),
        source_search=FakeSourceSearch([
            {"image": "img", "url": "url"},
        ]),
    )

    state = {
        "analyze_result": json.dumps({
            "products": [{"title": "t1", "description": "d"}],
            "initial": {"message": "hi"},
            "final": {"message": "bye"},
        })
    }

    result = agent.search_source_node(state)

    product = result["result"]["products"][0]
    assert product["image"] == "img"
    assert product["url"] == "url"


def test_call_client_rejects_non_string_prompt() -> None:
    agent = SearchAgent(
        llm_model="model",
        llm_client=FakeLLMClient(""),
        hybrid_search=FakeHybridSearch([]),
        source_search=FakeSourceSearch([]),
    )

    try:
        agent.call_client(123)
    except ValueError as exc:
        assert "Prompt must be a string" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
