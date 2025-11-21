"""Content extraction from AI responses.

This module handles extracting different types of content from AI responses,
including structured data, JSON, code blocks, and pattern-specific content.
"""

import json
import re
import logging
from typing import Optional, Dict, List, Any, Union

logger = logging.getLogger(__name__)

class ContentExtractor:
    """Extracts structured content from AI responses."""

    def extract_structured_data(self, response: Union[str, Dict]) -> Dict[str, Any]:
        """Extract structured data from AI response.

        Args:
            response: The AI response to extract data from

        Returns:
            Dict containing extracted structured data
        """
        if isinstance(response, dict):
            if 'content' in response:
                text = response['content']
            elif 'results' in response:
                # Response already contains parsed results
                return response['results']
            else:
                text = str(response)
        else:
            text = str(response)

        structured_data = {}

        # Try to extract JSON first
        json_data = self._extract_json_from_text(text)
        if json_data:
            structured_data.update(json_data)

        # Extract specific content types
        pattern_data = self._extract_content_by_patterns(text)
        structured_data.update(pattern_data)

        return structured_data

    def _extract_json_from_text(self, text: str) -> Optional[Dict]:
        """Extract JSON from text response.

        Args:
            text: Text to extract JSON from

        Returns:
            Parsed JSON data or None if no valid JSON found
        """
        # Try direct JSON parsing first
        result = self._try_direct_json_parse(text)
        if result is not None:
            return result

        # Fall back to regex pattern extraction
        return self._extract_from_malformed_json(text)

    def _try_direct_json_parse(self, text: str) -> Optional[Dict]:
        """Try to parse text as direct JSON with nested checks."""
        try:
            parsed = json.loads(text.strip())

            # Check for nested 'results' key
            if isinstance(parsed, dict) and 'results' in parsed:
                return parsed['results']

            # Check for nested JSON strings in values
            if isinstance(parsed, dict):
                nested = self._extract_nested_json_strings(parsed)
                if nested is not None:
                    return nested

            return parsed
        except json.JSONDecodeError:
            return None

    def _extract_nested_json_strings(self, parsed_dict: Dict) -> Optional[Dict]:
        """Extract JSON from string values within a parsed dictionary."""
        for value in parsed_dict.values():
            if isinstance(value, str):
                try:
                    nested_json = json.loads(value)
                    if isinstance(nested_json, dict):
                        return nested_json.get('results', nested_json)
                except json.JSONDecodeError:
                    continue
        return None

    def _extract_content_by_patterns(self, text: str) -> Dict[str, str]:
        """Extract content using regex patterns.

        Args:
            text: Text to extract content from

        Returns:
            Dict with extracted content by type
        """
        extracted = {}

        # Define extraction patterns
        patterns = {
            'html': [
                r'```html\s*\n(.*?)\n```',
                r'```\s*\n(<!DOCTYPE html.*?</html>)\s*\n```',
                r'(<!DOCTYPE html.*?</html>)',
            ],
            'css': [
                r'```css\s*\n(.*?)\n```',
                r'```\s*\n([^{]*\{[^}]*\}[^{]*)\s*\n```',
            ],
            'javascript': [
                r'```javascript\s*\n(.*?)\n```',
                r'```js\s*\n(.*?)\n```',
                r'```\s*\n(function.*?)\s*\n```',
                r'```\s*\n(const.*?)\s*\n```',
                r'```\s*\n(let.*?)\s*\n```',
                r'```\s*\n(var.*?)\s*\n```',
            ],
            'markdown': [
                r'```markdown\s*\n(.*?)\n```',
                r'```md\s*\n(.*?)\n```',
            ],
            'sql': [
                r'```sql\s*\n(.*?)\n```',
            ],
            'python': [
                r'```python\s*\n(.*?)\n```',
                r'```py\s*\n(.*?)\n```',
            ]
        }

        for content_type, type_patterns in patterns.items():
            content = self._extract_from_code_blocks(text, content_type, type_patterns)
            if content:
                extracted[content_type] = content

        return extracted

    def _extract_from_code_blocks(
            self,
            text: str,
            language: str,
            patterns: Optional[List[str]] = None
    ) -> Optional[str]:
        """Extract content from code blocks.

        Args:
            text: Text to search in
            language: Language to extract
            patterns: Custom patterns to use

        Returns:
            Extracted content or None
        """
        if patterns is None:
            patterns = [f'```{language}\\s*\\n(.*?)\\n```']

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE | re.IGNORECASE)
            if matches:
                # Return the first match, cleaned
                content = matches[0].strip()
                return self.clean_escaped_content(content)

        return None

    def clean_escaped_content(self, content: str) -> str:
        """Clean escaped content.

        Args:
            content: Content to clean

        Returns:
            Cleaned content
        """
        if not content:
            return content

        # Remove common escape sequences
        content = content.replace('\\n', '\n')
        content = content.replace('\\t', '\t')
        content = content.replace('\\"', '"')
        content = content.replace("\\'", "'")
        content = content.replace('\\\\', '\\')

        return content.strip()

    def extract_command_from_response(self, response: Union[str, Dict]) -> Optional[str]:
        """Extract command from AI response.

        Args:
            response: AI response to extract command from

        Returns:
            Extracted command or None
        """
        if isinstance(response, dict):
            text = response.get('content', str(response))
        else:
            text = str(response)

        # Look for command patterns
        command_patterns = [
            r'```bash\s*\n(.*?)\n```',
            r'```shell\s*\n(.*?)\n```',
            r'```cmd\s*\n(.*?)\n```',
            r'COMMAND:\s*(.+)',
            r'Command:\s*(.+)',
            r'Execute:\s*(.+)',
        ]

        for pattern in command_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
            if matches:
                command = matches[0].strip()
                # Clean up multiline commands
                if '\n' in command:
                    lines = [line.strip() for line in command.split('\n') if line.strip()]
                    command = ' && '.join(lines)
                return command

        return None

    def _extract_from_malformed_json(self, text: str) -> Optional[Dict[str, str]]:
        """Extract content from malformed JSON using regex patterns.

        This method attempts to extract key-value pairs from JSON-like text
        even when the JSON is malformed due to unescaped quotes or other issues.

        Args:
            text: The malformed JSON text

        Returns:
            Dict with extracted content or None if nothing found
        """
        extracted = {}

        # Look for the "results" section
        results_match = re.search(r'"results"\s*:\s*\{(.*)', text, re.DOTALL)
        if not results_match:
            return None

        results_content = results_match.group(1)

        # Extract key-value pairs from the results section
        # This pattern looks for "key": "value" pairs, handling escaped quotes and newlines
        pattern = r'"([^"]+)"\s*:\s*"((?:[^"\\]|\\.)*)(?:"|$)'
        matches = re.findall(pattern, results_content, re.DOTALL)

        for key, value in matches:
            # Unescape the value
            value = value.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
            extracted[key] = value

        return extracted if extracted else None
