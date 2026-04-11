"""
Model provider abstractions and implementations.

Contains providers for loading model configurations from various sources.
"""
from pathlib import Path

from src.interfaces import ModelProviderInterface
from src.utils import FileUtils


class CustomModelProvider(ModelProviderInterface):
    """
    YAML file-based model configuration provider.
    
    Loads model names and configurations from YAML files, allowing
    easy configuration changes without code modifications.
    """
    
    def __init__(self, model_file_path: str) -> None:
        """
        Initialize YAML model provider.
        
        Args:
            model_file_path: Path to the YAML configuration file
        """
        self._model_file_path = model_file_path

    def get_model_name(self) -> str:
        """
        Get the LLM model name from YAML configuration.
        
        Returns:
            The model name as configured in the YAML file
        """
        model_data = FileUtils.load_yaml(self._model_file_path)
        return model_data["LLM"]


def default_model_path() -> str:
    """
    Get the default model configuration file path.
    
    Returns the path to model.yaml in project root, relative to the
    chambot-server root directory.
    
    Returns:
        Path string to the default model configuration file
    """
    root = Path(__file__).resolve().parents[2]  # adapters -> src -> chatbot-server
    return str(root / "model.yaml")
