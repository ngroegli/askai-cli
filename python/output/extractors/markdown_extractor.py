"""
Markdown content extractor.
"""

import re
from typing import Optional

from .base_extractor import BaseExtractor
from ..common import unescape_string, find_largest_match


class MarkdownExtractor(BaseExtractor):
    """Markdown content extractor that specializes in finding markdown in AI responses."""
    
    def extract(self, response, output_name: Optional[str] = None) -> Optional[str]:
        """Extract markdown content using multiple strategies.
        
        Args:
            response: The full response (text or dict)
            output_name: Optional name of the output
            
        Returns:
            str: Extracted markdown content or None
        """
        # Handle dictionary responses
        if isinstance(response, dict):
            # Try to get content directly from the dict
            if output_name and output_name in response:
                content = response[output_name]
                if isinstance(content, str):
                    return content
            # Try common markdown field names
            if "markdown_content" in response:
                content = response["markdown_content"]
                if isinstance(content, str):
                    return content
            elif "markdown" in response:
                content = response["markdown"]
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
            output_name = "markdown_content"
        # Strategy 1: Try markdown sections by name
        section_result = self._extract_from_section(response, output_name)
        if section_result and len(section_result) > 50:
            if self.logger:
                self.logger.info(f"Found markdown content via section: {len(section_result)} chars")
            return section_result
        
        # Strategy 2: Try to find any markdown sections
        any_section_result = self._extract_any_markdown_section(response)
        if any_section_result and len(any_section_result) > 50:
            if self.logger:
                self.logger.info(f"Found markdown content via any section: {len(any_section_result)} chars")
            return any_section_result
        
        # Strategy 3: Try JSON extraction
        json_result = self._extract_from_json(response, output_name)
        if json_result and len(json_result) > 50:
            if self.logger:
                self.logger.info(f"Found markdown content via JSON extraction: {len(json_result)} chars")
            return json_result
        
        # Strategy 4: Try to detect markdown patterns
        md_pattern_result = self._detect_markdown_patterns(response)
        if md_pattern_result and len(md_pattern_result) > 50:
            if self.logger:
                self.logger.info(f"Found markdown content via pattern detection: {len(md_pattern_result)} chars")
            return md_pattern_result
        
        return None

    def _extract_any_markdown_section(self, response) -> Optional[str]:
        """Extract any markdown section from the text.
        
        Args:
            response: The full response (text or dict)
            
        Returns:
            str: Extracted markdown content or None
        """
        if not isinstance(response, str):
            try:
                response = str(response)
            except Exception:
                return None
                
        # Look for any markdown section headers
        pattern = r'(#{1,3}\s+.+?\n[\s\S]*?)(?=#{1,3}\s+|$)'
        matches = re.findall(pattern, response, re.MULTILINE)
        
        if matches:
            largest_match = find_largest_match(matches, min_length=50)
            if largest_match:
                return unescape_string(largest_match.strip())
        
        return None

    def _detect_markdown_patterns(self, response) -> Optional[str]:
        """Detect patterns that look like markdown formatting.
        
        Args:
            response: The full response (text or dict)
            
        Returns:
            str: Extracted markdown content or None
        """
        if not isinstance(response, str):
            try:
                response = str(response)
            except Exception:
                return None
        # Check for common markdown patterns
        md_patterns = [
            r'#+\s+.+',  # Headers
            r'\*\*.+?\*\*',  # Bold
            r'__.+?__',  # Bold alternative
            r'\*.+?\*',  # Italic
            r'_.+?_',  # Italic alternative
            r'```[\s\S]*?```',  # Code blocks
            r'>\s+.+',  # Blockquotes
            r'- .+',  # Unordered lists
            r'\d+\. .+',  # Ordered lists
            r'\[.+?\]\(.+?\)',  # Links
        ]
        
        # Count how many markdown patterns we find
        pattern_count = 0
        for pattern in md_patterns:
            matches = re.findall(pattern, response, re.MULTILINE)
            pattern_count += len(matches)
        
        # If we have enough markdown patterns, extract a reasonable chunk of the text
        if pattern_count >= 3:
            # Look for the "richest" part of the text with the most markdown formatting
            lines = response.split('\n')
            best_section_start = 0
            best_section_end = len(lines)
            best_pattern_density = 0
            
            # Analyze windows of lines to find the best section
            window_size = min(30, len(lines))  # Look at 30 lines at a time
            
            for i in range(len(lines) - window_size + 1):
                window = '\n'.join(lines[i:i+window_size])
                window_pattern_count = 0
                
                for pattern in md_patterns:
                    matches = re.findall(pattern, window, re.MULTILINE)
                    window_pattern_count += len(matches)
                
                pattern_density = window_pattern_count / window_size
                if pattern_density > best_pattern_density:
                    best_pattern_density = pattern_density
                    best_section_start = i
                    best_section_end = i + window_size
            
            # Extract the section with the highest markdown pattern density
            best_content = '\n'.join(lines[best_section_start:best_section_end])
            
            # If the pattern density is good enough, return this content
            if best_pattern_density > 0.2:  # At least 20% of lines should have markdown patterns
                return unescape_string(best_content)
        
        return None
