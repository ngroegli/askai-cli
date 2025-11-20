"""
JSON writer for handling JSON data.
"""

import json
import re
from typing import Optional, Dict, Any
from .base import BaseWriter


class JsonWriter(BaseWriter):
    """Writer for JSON content."""

    def can_handle(self, content_type: str) -> bool:
        """Check if this writer can handle the content type.

        Args:
            content_type: Type of content to check

        Returns:
            bool: True for JSON type
        """
        return content_type.lower() == 'json'

    def write(self, content: str, file_path: str,
              additional_params: Optional[Dict[str, Any]] = None) -> bool:
        """Write JSON content to file with proper formatting.

        Args:
            content: JSON content to write
            file_path: Path where to write the file
            additional_params: Additional parameters (e.g., indent level)

        Returns:
            bool: True if successful, False otherwise
        """
        cleaned_content = self._clean_content(content)
        formatted_content = self._format_json(cleaned_content, additional_params)

        # Ensure proper file extension
        if not file_path.lower().endswith('.json'):
            file_path += '.json'

        return self._write_file(formatted_content, file_path)

    def _format_json(self, content: str, additional_params: Optional[Dict[str, Any]] = None) -> str:
        """Format JSON content with proper structure.

        Args:
            content: JSON content to format
            additional_params: Additional parameters like indent level

        Returns:
            str: Formatted JSON content
        """
        # Extract indent level from additional params
        indent = 2
        if additional_params:
            indent = additional_params.get('indent', 2)

        # Remove JSON code block markers
        content = re.sub(r'^```json\\s*', '', content)
        content = re.sub(r'\\s*```$', '', content)

        try:
            # Parse and reformat JSON
            parsed_json = json.loads(content)
            formatted_json = json.dumps(parsed_json, indent=indent, ensure_ascii=False, sort_keys=True)
            self.logger.info(f"Successfully formatted JSON with indent={indent}")
            return formatted_json

        except json.JSONDecodeError as e:
            self.logger.warning(f"Invalid JSON format: {e}")

            # Try to fix common JSON issues
            fixed_content = self._fix_common_json_issues(content)

            try:
                parsed_json = json.loads(fixed_content)
                formatted_json = json.dumps(parsed_json, indent=indent, ensure_ascii=False, sort_keys=True)
                self.logger.info("Successfully formatted JSON after fixing common issues")
                return formatted_json

            except json.JSONDecodeError:
                self.logger.error("Could not fix JSON format, returning original content")
                return content

    def _fix_common_json_issues(self, content: str) -> str:
        """Fix common JSON formatting issues.

        Args:
            content: JSON content to fix

        Returns:
            str: Fixed JSON content
        """
        # Remove trailing commas
        content = re.sub(r',\\s*([}\\]])', r'\\1', content)

        # Fix single quotes to double quotes
        content = re.sub(r"'([^']*)':", r'"\\1":', content)
        content = re.sub(r"'([^']*)'", r'"\\1"', content)

        # Fix unquoted keys
        content = re.sub(r'(\\w+):', r'"\\1":', content)

        # Remove duplicate commas
        content = re.sub(r',\\s*,', r',', content)

        # Remove comments (not valid JSON but sometimes present)
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\\*.*?\\*/', '', content, flags=re.DOTALL)

        return content
