import yaml
from typing import Any, Dict, List, Union

class FileUtils:
    """
    Utility class providing file operations for the PickSmart application.
    
    This class contains static methods for common file operations like
    loading configuration files in various formats.
    """

    @staticmethod
    def load_yaml(file_path: str) -> Union[Dict[str, Any], List[Any]]:
        """
        Load and parse a YAML file into a Python object.
        
        Args:
            file_path: Path to the YAML file to be loaded
            
        Returns:
            The parsed YAML content as Python objects (typically dict or list)
            
        Raises:
            FileNotFoundError: If the specified file does not exist
            yaml.YAMLError: If the YAML file has invalid syntax
            IOError: If there are issues reading the file
        """
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            return data
