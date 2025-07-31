"""
JSON writer class for writing JSON content to files.
"""

import json
import re
from typing import Optional, Dict, List, Any, Union

from .base_writer import BaseWriter


class JsonWriter(BaseWriter):
    """JSON writer that handles JSON file writing with proper formatting."""
    
    def write_json(self, content: Union[str, Dict, List], file_path: str, pretty: bool = True) -> bool:
        """Write JSON content to a file with proper formatting.
        
        Args:
            content: JSON content to write (string or Python object)
            file_path: Path where to write the file
            pretty: Whether to format the JSON output with indentation
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure file has .json extension
        if not file_path.lower().endswith('.json'):
            file_path += '.json'
        
        # Parse string content into Python object if needed
        if isinstance(content, str):
            try:
                # Try to parse the string as JSON
                content_obj = self._parse_json_content(content)
            except json.JSONDecodeError:
                if self.logger:
                    self.logger.error("Failed to parse JSON content")
                return False
        else:
            # Content is already a Python object
            content_obj = content
        
        # Convert back to string with proper formatting
        try:
            if pretty:
                formatted_content = json.dumps(content_obj, indent=2, sort_keys=False)
            else:
                formatted_content = json.dumps(content_obj, sort_keys=False)
        except (TypeError, ValueError) as e:
            if self.logger:
                self.logger.error(f"Failed to convert JSON object to string: {str(e)}")
            return False
        
        return self.write(formatted_content, file_path)
    
    def _parse_json_content(self, content: str) -> Union[Dict, List]:
        """Parse JSON string content into a Python object.
        
        Args:
            content: JSON content as a string
            
        Returns:
            Union[Dict, List]: Parsed JSON as a Python object
        
        Raises:
            json.JSONDecodeError: If the content cannot be parsed as JSON
        """
        # Remove code block markers if present
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        
        # Try to parse the JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Try to fix common JSON errors
            content = self._fix_common_json_errors(content)
            return json.loads(content)  # If this fails, let the error propagate
    
    def _fix_common_json_errors(self, content: str) -> str:
        """Fix common JSON formatting errors.
        
        Args:
            content: JSON content to fix
            
        Returns:
            str: Fixed JSON content
        """
        # Replace single quotes with double quotes (except within strings)
        # This is a simplistic approach and won't handle all cases correctly
        content = re.sub(r"(?<!\")\'(?!\")", '"', content)
        
        # Fix missing quotes around property names
        content = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', content)
        
        # Replace trailing commas in arrays and objects
        content = re.sub(r',\s*}', '}', content)
        content = re.sub(r',\s*]', ']', content)
        
        if self.logger:
            self.logger.info("Fixed common JSON formatting errors")
        
        return content
