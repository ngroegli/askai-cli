"""
JSON content extractor.
"""

import re
import json
from typing import Optional, Any, Dict, Union, List

from .base_extractor import BaseExtractor


class JsonExtractor(BaseExtractor):
    """JSON content extractor that specializes in finding JSON data in AI responses."""
    
    def extract(self, response, output_name: Optional[str] = None) -> Optional[Union[Dict[str, Any], List[Any], str]]:
        """Extract JSON data using multiple strategies.
        
        Args:
            response: The full response (can be text or dict)
            output_name: Optional name of the output
            
        Returns:
            Optional[Union[Dict[str, Any], List[Any], str]]: Extracted JSON data or None
        """
        # Handle dictionary responses
        if isinstance(response, dict):
            # If a specific field name is provided, try to extract just that field
            if output_name and output_name in response:
                return response[output_name]
            # Otherwise return the entire dict
            return response
            
        # Make sure response is a string for regex operations
        if not isinstance(response, str):
            try:
                response = str(response)
            except Exception:
                return None
                
        # Strategy 1: Try code blocks with JSON language
        code_block_result = self._extract_json_from_code_blocks(response)
        if code_block_result:
            if self.logger:
                self.logger.info("Found JSON content via code blocks")
            return code_block_result
        
        # Strategy 2: Try finding any valid JSON objects in the text
        json_obj_result = self._extract_json_objects(response)
        if json_obj_result:
            if self.logger:
                self.logger.info("Found JSON content via object detection")
            return json_obj_result
        
        # Strategy 3: Try specific patterns for common API responses
        api_result = self._extract_api_json(response)
        if api_result:
            if self.logger:
                self.logger.info("Found JSON content via API pattern detection")
            return api_result
        
        return None

    def _extract_json_from_code_blocks(self, response) -> Optional[Dict[str, Any]]:
        """Extract JSON from code blocks.
        
        Args:
            response: The full response text or dict
            
        Returns:
            Dict[str, Any]: Extracted JSON data or None
        """
        if isinstance(response, dict):
            return response
            
        if not isinstance(response, str):
            try:
                response = str(response)
            except Exception:
                return None
                
        patterns = [
            r'```json\s*\n([\s\S]*?)\n```',
            r'```\s*\n(\{[\s\S]*?\})\n```',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue
        
        return None

    def _extract_json_objects(self, response) -> Optional[Dict[str, Any]]:
        """Extract any JSON objects from the text.
        
        Args:
            response: The full response (text or dict)
            
        Returns:
            Dict[str, Any]: Extracted JSON data or None
        """
        if isinstance(response, dict):
            return response
            
        if not isinstance(response, str):
            try:
                response = str(response)
            except Exception:
                return None
                
        # Find potential JSON objects (from { to matching })
        def find_json_objects(text):
            result = []
            brace_count = 0
            start_idx = -1
            
            for i, char in enumerate(text):
                if char == '{':
                    if brace_count == 0:
                        start_idx = i
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0 and start_idx != -1:
                        result.append(text[start_idx:i+1])
                        start_idx = -1
            
            return result
        
        json_candidates = find_json_objects(response)
        
        for candidate in json_candidates:
            try:
                data = json.loads(candidate)
                if isinstance(data, dict) and len(data) > 0:
                    return data
            except json.JSONDecodeError:
                continue
        
        return None

    def _extract_api_json(self, response) -> Optional[Dict[str, Any]]:
        """Extract JSON that looks like API responses.
        
        Args:
            response: The full response (text or dict)
            
        Returns:
            Dict[str, Any]: Extracted JSON data or None
        """
        if isinstance(response, dict):
            return response
            
        if not isinstance(response, str):
            try:
                response = str(response)
            except Exception:
                return None
                
        # Look for common API response patterns
        patterns = [
            r'(?:Response|Result|Output):\s*(\{[\s\S]*?\})',
            r'```(?:json)?\s*\n(\{[\s\S]*?"(?:data|result|response)":\s*\{[\s\S]*?\}[\s\S]*?\})\s*\n```',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue
        
        return None
