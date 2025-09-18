"""Response normalization and cleaning.

This module handles normalizing AI responses from different formats
and cleaning content for processing.
"""

import json
import logging
from typing import Union, Dict

logger = logging.getLogger(__name__)

class ResponseNormalizer:
    """Normalizes and cleans AI responses."""

    def normalize_response(self, response: Union[str, Dict]) -> str:
        """Normalize response to a consistent string format.

        Args:
            response: Raw response from AI service

        Returns:
            Normalized string response
        """
        if isinstance(response, dict):
            # Handle OpenRouter response format
            if 'choices' in response and response['choices']:
                choice = response['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    return choice['message']['content']
                if 'text' in choice:
                    return choice['text']

            # Handle direct content format
            if 'content' in response:
                return response['content']

            # Handle result format
            if 'result' in response:
                if isinstance(response['result'], str):
                    return response['result']
                return json.dumps(response['result'], indent=2)

            # Handle raw message format
            if 'message' in response and isinstance(response['message'], dict):
                if 'content' in response['message']:
                    return response['message']['content']

            # Fall back to JSON representation
            try:
                return json.dumps(response, indent=2)
            except (TypeError, ValueError):
                return str(response)

        if isinstance(response, str):
            return response
        # Handle other types
        try:
            return json.dumps(response, indent=2)
        except (TypeError, ValueError):
            return str(response)

    def clean_content(self, content: str) -> str:
        """Clean and format content.

        Args:
            content: Content to clean

        Returns:
            Cleaned content
        """
        if not content:
            return content

        # Remove excessive whitespace
        content = content.strip()

        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        # Remove trailing whitespace from lines
        lines = content.split('\n')
        lines = [line.rstrip() for line in lines]
        content = '\n'.join(lines)

        return content
