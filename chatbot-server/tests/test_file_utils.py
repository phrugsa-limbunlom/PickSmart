from pathlib import Path

import pytest

from src.utils.file_utils import FileUtils


def test_load_yaml_reads_file(tmp_path: Path) -> None:
    data = {"LLM": "test-model", "items": [1, 2]}
    file_path = tmp_path / "config.yaml"
    file_path.write_text("LLM: test-model\nitems:\n  - 1\n  - 2\n", encoding="utf-8")

    result = FileUtils.load_yaml(str(file_path))

    assert result == data


def test_load_yaml_missing_file_raises(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError):
        FileUtils.load_yaml(str(missing_path))
