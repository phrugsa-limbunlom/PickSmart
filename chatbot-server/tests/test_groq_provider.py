import types

import pytest

from src.adapters.llm.groq_provider import GroqProvider


class FakeGroqClient:
    def __init__(self):
        self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        message = types.SimpleNamespace(content="hello")
        choice = types.SimpleNamespace(message=message)
        return types.SimpleNamespace(choices=[choice])


def test_groq_provider_generates_response(monkeypatch) -> None:
    monkeypatch.setattr("src.adapters.llm.groq_provider.Groq", lambda api_key: FakeGroqClient())
    provider = GroqProvider(api_key="key")

    result = provider.generate(prompt="ping", model="model")

    assert result == "hello"


def test_groq_provider_rejects_non_string_prompt(monkeypatch) -> None:
    monkeypatch.setattr("src.adapters.llm.groq_provider.Groq", lambda api_key: FakeGroqClient())
    provider = GroqProvider(api_key="key")

    with pytest.raises(ValueError):
        provider.generate(prompt=123, model="model")
