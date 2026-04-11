from pathlib import Path

from src.adapters.model_provider import CustomModelProvider, default_model_path


def test_custom_model_provider_reads_model_name(monkeypatch) -> None:
    def fake_load_yaml(path: str):
        return {"LLM": "unit-test-model"}

    monkeypatch.setattr("src.adapters.model_provider.FileUtils.load_yaml", fake_load_yaml)

    provider = CustomModelProvider("/fake/path.yaml")

    assert provider.get_model_name() == "unit-test-model"


def test_default_model_path_points_to_root() -> None:
    model_path = default_model_path()
    path = Path(model_path)

    assert path.name == "model.yaml"
    assert "chatbot-server" in path.as_posix()
