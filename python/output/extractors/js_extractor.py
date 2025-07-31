"""
JavaScript content extractor.
"""

import re
from typing import Optional

from .base_extractor import BaseExtractor
from ..common import unescape_string, find_largest_match


class JsExtractor(BaseExtractor):
    """JavaScript content extractor that specializes in finding JS code in AI responses."""
    
    def extract(self, response, output_name: Optional[str] = None) -> Optional[str]:
        """Extract JavaScript content using multiple strategies.
        
        Args:
            response: The full response (can be text or dict)
            output_name: Optional name of the output
            
        Returns:
            str: Extracted JavaScript content or None
        """
        # Handle dictionary responses
        if isinstance(response, dict):
            # Try to get content directly from the dict
            if output_name and output_name in response:
                content = response[output_name]
                if isinstance(content, str):
                    return content
            # Try common JS field names
            if "javascript_code" in response:
                content = response["javascript_code"]
                if isinstance(content, str):
                    return content
            elif "javascript" in response:
                content = response["javascript"]
                if isinstance(content, str):
                    return content
            elif "js_code" in response:
                content = response["js_code"]
                if isinstance(content, str):
                    return content
            # Try to convert dict to string for further processing
            try:
                import json
                response_str = json.dumps(response)
                return self.extract(response_str, output_name)
            except Exception:
                return None
                
        # Make sure we're working with a string
        if not isinstance(response, str):
            response = str(response)
            
        # Default output name if none provided
        if output_name is None:
            output_name = "javascript"
        # Strategy 1: Try JSON extraction first (most reliable)
        json_result = self._extract_from_json(response, output_name)
        if json_result and len(json_result) > 50:
            if self.logger:
                self.logger.info(f"Found JS content via JSON extraction: {len(json_result)} chars")
            return json_result
        
        # Strategy 2: Try code blocks with js/javascript language
        for language in ["js", "javascript"]:
            code_block_result = self._extract_from_code_blocks(response, language=language)
            if code_block_result and len(code_block_result) > 50:
                if self.logger:
                    self.logger.info(f"Found JS content via code blocks: {len(code_block_result)} chars")
                return code_block_result
        
        # Strategy 3: Try markdown sections
        section_result = self._extract_from_section(response, output_name)
        if section_result and len(section_result) > 50:
            if self.logger:
                self.logger.info(f"Found JS content via markdown section: {len(section_result)} chars")
            return section_result
        
        # Strategy 4: Try script tags
        script_result = self._extract_from_script_tags(response)
        if script_result and len(script_result) > 50:
            if self.logger:
                self.logger.info(f"Found JS content via script tags: {len(script_result)} chars")
            return script_result
        
        # Strategy 5: Try detecting JS patterns
        js_pattern_result = self._extract_js_patterns(response)
        if js_pattern_result and len(js_pattern_result) > 50:
            if self.logger:
                self.logger.info(f"Found JS content via pattern detection: {len(js_pattern_result)} chars")
            return js_pattern_result
        
        return None

    def _extract_from_script_tags(self, response: str) -> Optional[str]:
        """Extract JavaScript from script tags.
        
        Args:
            response: The full response text
            
        Returns:
            str: Extracted JavaScript or None
        """
        pattern = r'<script[^>]*>\s*([\s\S]*?)\s*</script>'
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            largest_match = find_largest_match(matches, min_length=50)
            if largest_match:
                return unescape_string(largest_match.strip())
        
        return None

    def _extract_js_patterns(self, response: str) -> Optional[str]:
        """Extract content that looks like JavaScript code.
        
        Args:
            response: The full response text
            
        Returns:
            str: Extracted JavaScript or None
        """
        # Common JavaScript patterns
        patterns = [
            r'(?:function|const|let|var|class|import|export)[\s\S]*?(?:\{[\s\S]*?\})',
            r'document\.(?:getElementById|querySelector|addEventListener)[\s\S]*?(?:\{[\s\S]*?\})',
            r'(?:async|function)\s+\w+\s*\([\s\S]*?\)\s*\{[\s\S]*?\}',
            r'\(\s*function\s*\(\)\s*\{[\s\S]*?\}\s*\)\(\);',
        ]
        
        js_blocks = []
        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            js_blocks.extend(matches)
        
        if js_blocks:
            # Sort by length to get the most substantial JS content
            js_blocks.sort(key=len, reverse=True)
            
            # Take the largest block if it's substantial
            if js_blocks and len(js_blocks[0]) > 100:
                return unescape_string(js_blocks[0])
                
            # If no single block is large enough, try combining blocks
            if len(js_blocks) > 1:
                combined_js = "\n\n".join(block.strip() for block in js_blocks if len(block.strip()) > 20)
                if len(combined_js) > 100:
                    return unescape_string(combined_js)
        
        return None
