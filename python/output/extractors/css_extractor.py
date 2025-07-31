"""
CSS content extractor.
"""

import re
import json
from typing import Optional, List

from .base_extractor import BaseExtractor
from ..common import unescape_string, find_largest_match


class CssExtractor(BaseExtractor):
    """CSS content extractor that uses multiple strategies to find CSS content."""
    
    def extract(self, response, output_name: Optional[str] = None) -> Optional[str]:
        """Extract CSS content using multiple strategies.
        
        Args:
            response: The full response (can be text or dict)
            output_name: Optional name of the output (usually 'css_styles')
            
        Returns:
            str: Extracted CSS content or None
        """
        # Handle dictionary responses
        if isinstance(response, dict):
            # Try to get content directly from the dict
            if output_name and output_name in response:
                content = response[output_name]
                if isinstance(content, str):
                    return content
            # Try common CSS field names
            if "css_styles" in response:
                content = response["css_styles"]
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
            output_name = "css_styles"
        # Strategy 1: Try JSON extraction first (most reliable)
        json_result = self._extract_from_json(response, output_name)
        if json_result and len(json_result) > 50:
            if self.logger:
                self.logger.info(f"Found CSS content via JSON extraction: {len(json_result)} chars")
            return json_result
        
        # Strategy 2: Try code blocks
        code_block_result = self._extract_from_code_blocks(response, language="css")
        if code_block_result and len(code_block_result) > 50:
            if self.logger:
                self.logger.info(f"Found CSS content via code blocks: {len(code_block_result)} chars")
            return code_block_result
        
        # Strategy 3: Try style tags
        style_result = self._extract_from_style_tags(response)
        if style_result and len(style_result) > 50:
            if self.logger:
                self.logger.info(f"Found CSS content via style tags: {len(style_result)} chars")
            return style_result
        
        # Strategy 4: Try markdown sections
        section_result = self._extract_from_section(response, output_name)
        if section_result and len(section_result) > 50:
            if self.logger:
                self.logger.info(f"Found CSS content via markdown section: {len(section_result)} chars")
            return section_result
        
        # Strategy 5: Try direct patterns for JSON field extraction
        json_field_result = self._extract_from_json_fields(response, output_name)
        if json_field_result and len(json_field_result) > 50:
            if self.logger:
                self.logger.info(f"Found CSS content via JSON fields: {len(json_field_result)} chars")
            return json_field_result
        
        # Strategy 6: Try direct CSS rule extraction
        css_rule_result = self._extract_css_rules(response)
        if css_rule_result and len(css_rule_result) > 50:
            if self.logger:
                self.logger.info(f"Found CSS content via rule extraction: {len(css_rule_result)} chars")
            return css_rule_result
        
        # Strategy 7: Try reconstructing from CSS properties
        css_prop_result = self._extract_css_properties(response)
        if css_prop_result and len(css_prop_result) > 50:
            if self.logger:
                self.logger.info(f"Found CSS content via property extraction: {len(css_prop_result)} chars")
            return css_prop_result
        
        return None

    def _extract_from_style_tags(self, response: str) -> Optional[str]:
        """Extract CSS content from style tags.
        
        Args:
            response: The full response text
            
        Returns:
            str: Extracted CSS content or None
        """
        pattern = r'<style>\s*([\s\S]*?)\s*</style>'
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            largest_match = find_largest_match(matches, min_length=50)
            if largest_match:
                return unescape_string(largest_match.strip())
        
        return None

    def _extract_from_json_fields(self, response: str, output_name: str) -> Optional[str]:
        """Extract CSS content directly from JSON field patterns.
        
        Args:
            response: The full response text
            output_name: Name of the output field
            
        Returns:
            str: Extracted CSS content or None
        """
        css_json_patterns = [
            rf'"{re.escape(output_name)}"\s*:\s*"([\s\S]*?)(?:"|$)',  # Double quotes
            rf"'{re.escape(output_name)}'\s*:\s*'([\s\S]*?)(?:'|$)",  # Single quotes
            rf'{re.escape(output_name)}[\'"]?\s*:\s*[\'"`]([\s\S]*?)[\'"`]\s*[,}}]',  # Field extraction
        ]
        
        for pattern in css_json_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            if matches:
                largest_match = find_largest_match(matches, min_length=50)
                if largest_match:
                    return unescape_string(largest_match)
        
        return None

    def _extract_css_rules(self, response: str) -> Optional[str]:
        """Extract CSS rules from the response.
        
        Args:
            response: The full response text
            
        Returns:
            str: Extracted CSS content or None
        """
        css_indicators = [
            # Complete CSS document pattern with multiple rules
            r'(?:body|html|div|header|footer|main|section|nav|h[1-6]|p|a|ul|ol|li|img|span|button|input|form)[\s\n]*\{[\s\S]*?\}(?:[\s\S]*?\{[\s\S]*?\})*',
            
            # CSS rule blocks including comments
            r'(?:\/\*[\s\S]*?\*\/)?[\s\n]*[a-zA-Z0-9\s\.\#\[\]\=\"\'\^\*\:\>\+\~\,\_\-]+\{[\s\S]*?\}',
            
            # Common CSS at-rules
            r'(?:@media|@keyframes|@font-face)[\s\S]*?\{[\s\S]*?\}',
            
            # Stylesheet with multiple rules
            r'(?:\/\*[\s\S]*?\*\/)?[\s\n]*(?:[a-zA-Z0-9\s\.\#\[\]\=\"\'\^\*\:\>\+\~\,\_\-]+\{[\s\S]*?\}[\s\n]*)+',
        ]
        
        # Find all potential CSS content
        css_blocks = []
        for pattern in css_indicators:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                # Only add if it looks like valid CSS
                if '{' in match and '}' in match and ':' in match:
                    css_blocks.append(match.strip())
        
        if css_blocks:
            # Sort blocks by length to find the most substantial CSS content
            css_blocks.sort(key=len, reverse=True)
            
            # Take the largest block if it's substantial
            if css_blocks and len(css_blocks[0]) > 100:
                return unescape_string(css_blocks[0])
                
            # If no single block is large enough, try combining valid blocks
            valid_blocks = []
            for block in css_blocks:
                block_clean = block.strip()
                # Ensure it looks like valid CSS with selectors and properties
                if re.search(r'[a-zA-Z0-9\s\.\#\[\]]+\s*\{[^{}]*:[^{}]*;\s*[^{}]*\}', block_clean, re.DOTALL):
                    valid_blocks.append(block_clean)
            
            if valid_blocks:
                combined_css = '\n\n'.join(valid_blocks)
                if len(combined_css) > 100:
                    return unescape_string(combined_css)
        
        return None

    def _extract_css_properties(self, response: str) -> Optional[str]:
        """Extract individual CSS properties and reconstruct a CSS file.
        
        Args:
            response: The full response text
            
        Returns:
            str: Reconstructed CSS content or None
        """
        css_properties = re.findall(r'([a-zA-Z\-]+)\s*:\s*([^;]+);', response, re.DOTALL)
        if len(css_properties) > 5:  # Need at least a few properties to be valid CSS
            reconstructed_css = "body {\n"
            for prop, value in css_properties:
                reconstructed_css += f"  {prop}: {value};\n"
            reconstructed_css += "}\n"
            return reconstructed_css
        
        return None
