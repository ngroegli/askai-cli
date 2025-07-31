"""
HTML content extractor.
"""

import re
from typing import Optional, Any

from .base_extractor import BaseExtractor
from ..common import unescape_string, find_largest_match


class HtmlExtractor(BaseExtractor):
    """HTML content extractor that specializes in finding HTML content in AI responses."""
    
    def extract(self, response: Any, output_name: Optional[str] = None) -> Optional[str]:
        """Extract HTML content using multiple strategies.
        
        Args:
            response: The full response (can be text or dict)
            output_name: Optional name of the output
            
        Returns:
            str: Extracted HTML content or None
        """
        # Handle dictionary responses
        if isinstance(response, dict):
            # Try to get content directly from the dict
            if output_name and output_name in response:
                content = response[output_name]
                if isinstance(content, str):
                    return content
            # Try common HTML field names
            if "html_content" in response:
                content = response["html_content"]
                if isinstance(content, str):
                    return content
            # Try to convert dict to string for further processing
            try:
                import json
                response_str = json.dumps(response)
                return self.extract(response_str, output_name)
            except Exception:
                return None
        
        if not isinstance(response, str):
            response = str(response)
        
        # Default output name if none provided
        if output_name is None:
            output_name = "html_content"
            
        # Strategy 1: Try JSON extraction first (most reliable)
        json_result = self._extract_from_json(response, output_name)
        if json_result and len(json_result) > 50:
            if self.logger:
                self.logger.info(f"Found HTML content via JSON extraction: {len(json_result)} chars")
            return json_result
        
        # Strategy 2: Try code blocks
        code_block_result = self._extract_from_code_blocks(response, language="html")
        if code_block_result and len(code_block_result) > 50:
            if self.logger:
                self.logger.info(f"Found HTML content via code blocks: {len(code_block_result)} chars")
            return code_block_result
        
        # Strategy 3: Try markdown sections
        section_result = self._extract_from_section(response, output_name)
        if section_result and len(section_result) > 50:
            if self.logger:
                self.logger.info(f"Found HTML content via markdown section: {len(section_result)} chars")
            return section_result
        
        # Strategy 4: Try full HTML documents
        doc_result = self._extract_html_document(response)
        if doc_result and len(doc_result) > 50:
            if self.logger:
                self.logger.info(f"Found HTML content via document extraction: {len(doc_result)} chars")
            return doc_result
        
        return None
    
    def _extract_html_document(self, response: str) -> Optional[str]:
        """Extract a full HTML document.
        
        Args:
            response: The full response text
            
        Returns:
            str: Extracted HTML document or None
        """
        # Try to find a complete HTML document
        patterns = [
            r'<!DOCTYPE html>[\s\S]*?<html[\s\S]*?</html>',
            r'<html[\s\S]*?</html>',
            r'<body[\s\S]*?</body>',
            r'<div[\s\S]*?id=["\']\w+["\'][\s\S]*?</div>',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
            if matches:
                largest_match = find_largest_match(matches, min_length=100)
                if largest_match:
                    return unescape_string(largest_match)
        
        return None
