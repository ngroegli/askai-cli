"""
JavaScript writer class for writing JS content to files.
"""

import re
from typing import Optional, List, Dict

from .base_writer import BaseWriter


class JsWriter(BaseWriter):
    """JavaScript writer that handles JS file writing with appropriate formatting."""
    
    def write_js(self, content: str, file_path: str) -> bool:
        """Write JavaScript content to a file with proper formatting.
        
        Args:
            content: JavaScript content to write
            file_path: Path where to write the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure file has .js extension
        if not file_path.lower().endswith('.js'):
            file_path += '.js'
        
        # Clean up and format JavaScript content
        formatted_content = self._format_js_content(content)
        
        return self.write(formatted_content, file_path)
    
    def _format_js_content(self, js_content: str) -> str:
        """Format JavaScript content for proper output.
        
        Args:
            js_content: The JavaScript content to format
            
        Returns:
            str: Formatted JavaScript content
        """
        # Remove script tags if present
        js_content = re.sub(r'<script[^>]*>(.*?)</script>', r'\1', 
                           js_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Cleanup common formatting issues
        
        # Ensure semicolons at the end of statements if not already there
        # This is a simple heuristic and won't catch all cases
        js_content = re.sub(r'(\w+|\)|\]|\})\s*$', r'\1;', js_content, flags=re.MULTILINE)
        
        # Fix missing semicolons before line breaks for common patterns
        js_content = re.sub(r'(\w+|\)|\]|\})\s*\n', r'\1;\n', js_content)
        
        # Don't add semicolons after blocks or if one already exists
        js_content = re.sub(r';\s*;', r';', js_content)
        js_content = re.sub(r'\}\s*;', r'}', js_content)
        
        # Ensure document.addEventListener for DOMContentLoaded if interacting with DOM
        if re.search(r'document\.getElementById|document\.querySelector|document\.getElement', js_content, re.IGNORECASE) and \
           not re.search(r'DOMContentLoaded', js_content, re.IGNORECASE):
            
            # Check if the content is already wrapped in a function or event listener
            if not re.search(r'^\s*\(\s*function|window\.onload|addEventListener', js_content.lstrip()):
                # Wrap the content in DOMContentLoaded event listener
                js_content = (
                    "document.addEventListener('DOMContentLoaded', function() {\n" +
                    self._indent_code(js_content) +
                    "\n});"
                )
                if self.logger:
                    self.logger.info("Added DOMContentLoaded wrapper for DOM interactions")
        
        # Add use strict if not present
        if not re.search(r"'use strict'|\"use strict\"", js_content):
            # If there's a DOMContentLoaded wrapper, add use strict inside it
            if re.search(r"document\.addEventListener\('DOMContentLoaded',", js_content):
                js_content = re.sub(
                    r"(document\.addEventListener\('DOMContentLoaded',\s*function\(\)\s*\{)\s*", 
                    r"\1\n  'use strict';\n  ", 
                    js_content
                )
            else:
                # Otherwise add it at the top
                js_content = "'use strict';\n\n" + js_content
                
            if self.logger:
                self.logger.info("Added 'use strict' directive")
        
        return js_content
    
    def _indent_code(self, code: str, spaces: int = 2) -> str:
        """Indent code by the specified number of spaces.
        
        Args:
            code: Code to indent
            spaces: Number of spaces for indentation
            
        Returns:
            str: Indented code
        """
        indent = ' ' * spaces
        return indent + code.replace('\n', '\n' + indent)
