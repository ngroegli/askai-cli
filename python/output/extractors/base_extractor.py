"""
Base extractor class for content extraction from AI responses.
"""

import re
import json
from typing import Optional, List, Dict, Any

from ..common import unescape_string, find_largest_match


class BaseExtractor:
    """Base class for content extraction from AI responses."""
    
    def __init__(self, logger=None):
        """Initialize the extractor.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger
    
    def extract(self, response, output_name: Optional[str] = None) -> Optional[str]:
        """Extract content from an AI response.
        
        Args:
            response: The AI response (can be text or a dictionary)
            output_name: Optional name of the output to extract
            
        Returns:
            Optional[str]: The extracted content, or None if not found
        """
        # Handle the case where response is a dictionary
        if isinstance(response, dict):
            if 'content' in response:
                return self.extract(response['content'], output_name)
            elif 'text' in response:
                return self.extract(response['text'], output_name)
            elif 'message' in response:
                return self.extract(response['message'], output_name)
            elif 'choices' in response and response['choices'] and isinstance(response['choices'], list):
                for choice in response['choices']:
                    if isinstance(choice, dict):
                        if 'message' in choice and 'content' in choice['message']:
                            return self.extract(choice['message']['content'], output_name)
                        elif 'text' in choice:
                            return self.extract(choice['text'], output_name)
            
            # As a last resort, try JSON serializing the dictionary and extracting from that
            import json
            try:
                return self.extract(json.dumps(response, indent=2), output_name)
            except:
                return None
                
        raise NotImplementedError("Subclasses must implement extract()")
    
    def _extract_from_code_blocks(self, response: str, language: str = None) -> Optional[str]:
        """Extract content from code blocks.
        
        Args:
            response: The AI response text
            language: Optional language identifier for the code block
            
        Returns:
            Optional[str]: The extracted content, or None if not found
        """
        patterns = []
        
        # If a specific language is provided, look for that first
        if language:
            patterns.append(rf'```{language}\s*\n([\s\S]*?)\n```')
        
        # Also try generic code blocks
        patterns.append(r'```\s*\n([\s\S]*?)\n```')
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            if matches:
                largest_match = find_largest_match(matches, min_length=20)
                if largest_match:
                    return unescape_string(largest_match.strip())
        
        return None
    
    def _extract_from_section(self, response: str, section_name: str) -> Optional[str]:
        """Extract content from markdown section headers.
        
        Args:
            response: The AI response text
            section_name: The name of the section to extract
            
        Returns:
            Optional[str]: The extracted content, or None if not found
        """
        pattern = rf'(?:##|###)\s*{re.escape(section_name)}.*?\n([\s\S]*?)(?=(?:##|###)|$)'
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            content = matches[0].strip()
            # Remove code block markers if present
            content = re.sub(r'^```.*?\n|```$', '', content, flags=re.DOTALL)
            return unescape_string(content.strip())
        
        return None
    
    def _extract_from_json(self, response, field_name: str) -> Optional[str]:
        """Extract content from JSON structures.
        
        Args:
            response: The AI response (can be text or dict)
            field_name: The name of the JSON field to extract
            
        Returns:
            Optional[str]: The extracted content, or None if not found
        """
        # If response is already a dictionary
        if isinstance(response, dict):
            if field_name in response:
                content = response[field_name]
                if isinstance(content, str):
                    return unescape_string(content)
                elif content is not None:
                    # Convert non-string content to string
                    return str(content)
            return None
            
        # Make sure response is a string for regex operations
        if not isinstance(response, str):
            try:
                response = str(response)
            except Exception:
                return None
                
        # Try to find JSON objects
        json_patterns = [
            r'```json\s*\n([\s\S]*?)\n```',  # Standard JSON code block
            r'\{[\s\S]*?"' + re.escape(field_name) + r'"\s*:\s*"[\s\S]*?"\s*[,}]',  # Direct JSON with field
            r'HERE THE RESULT:\s*```json\s*\n([\s\S]*?)\n```',
            r'HERE THE RESULT:\s*\n(\{[\s\S]*?})',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    # Clean up the match - some patterns might capture surrounding text
                    if match.strip().startswith('{'):
                        json_text = match.strip()
                    else:
                        # Find the JSON object in the text
                        json_start = match.find('{')
                        json_end = match.rfind('}') + 1
                        if json_start >= 0 and json_end > json_start:
                            json_text = match[json_start:json_end]
                        else:
                            continue
                    
                    json_data = json.loads(json_text)
                    if isinstance(json_data, dict) and field_name in json_data:
                        content = json_data[field_name]
                        if isinstance(content, str):
                            return unescape_string(content)
                except (json.JSONDecodeError, Exception):
                    continue
        
        # Try to extract directly from JSON field patterns
        field_patterns = [
            rf'"{re.escape(field_name)}"\s*:\s*"([\s\S]*?)(?:"|$)',  # Double quotes
            rf"'{re.escape(field_name)}'\s*:\s*'([\s\S]*?)(?:'|$)",  # Single quotes
        ]
        
        for pattern in field_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            if matches:
                largest_match = find_largest_match(matches, min_length=50)
                if largest_match:
                    return unescape_string(largest_match)
        
        return None
