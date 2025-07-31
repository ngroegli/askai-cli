"""
HTML writer class for writing HTML content to files.
"""

import re
from typing import Optional, List, Dict

from .base_writer import BaseWriter


class HtmlWriter(BaseWriter):
    """HTML writer that handles HTML file writing with references to other files."""
    
    def write_html(self, content: str, file_path: str, css_path: Optional[str] = None, 
                  js_path: Optional[str] = None) -> bool:
        """Write HTML content to a file with proper references to CSS and JS files.
        
        Args:
            content: HTML content to write
            file_path: Path where to write the file
            css_path: Optional path to CSS file to reference
            js_path: Optional path to JS file to reference
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure file has .html extension
        if not file_path.lower().endswith('.html'):
            file_path += '.html'
        
        # Fix HTML references
        fixed_content = self._validate_html_references(content, css_path, js_path)
        
        return self.write(fixed_content, file_path)
    
    def _validate_html_references(self, html_content: str, css_path: Optional[str] = None, 
                                 js_path: Optional[str] = None) -> str:
        """Validate and fix HTML file references to match output filenames.
        
        Args:
            html_content: The HTML content to validate
            css_path: Optional path to CSS file
            js_path: Optional path to JS file
            
        Returns:
            str: Validated HTML content with correct file references
        """
        # Make sure HTML has proper structure
        if not re.search(r'<html[^>]*>', html_content, re.IGNORECASE):
            html_content = f'<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Generated Page</title>\n</head>\n<body>\n{html_content}\n</body>\n</html>'
            if self.logger:
                self.logger.info("Added HTML structure to content")

        # Ensure there's a head section
        if not re.search(r'<head[^>]*>', html_content, re.IGNORECASE):
            # Add a head section before the body
            body_start = html_content.find('<body')
            if body_start != -1:
                html_content = html_content[:body_start] + '<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Generated Page</title>\n</head>\n' + html_content[body_start:]
                if self.logger:
                    self.logger.info("Added missing head section")
        
        # Fix CSS reference if found
        if css_path:
            # Extract just the filename without path
            css_filename = css_path.split('/')[-1]
            
            # First look for any existing stylesheet link
            has_css_link = bool(re.search(r'<link[^>]*rel=["\']stylesheet["\'][^>]*>', html_content, re.IGNORECASE))
            
            if has_css_link:
                # Replace any CSS reference with the correct filename
                html_content = re.sub(
                    r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\'][^"\']*["\'][^>]*>',
                    f'<link rel="stylesheet" href="{css_filename}">',
                    html_content,
                    flags=re.IGNORECASE
                )
                if self.logger:
                    self.logger.info(f"Updated CSS reference to: {css_filename}")
            else:
                # No CSS link found, add it to head
                head_end = html_content.find('</head>')
                if head_end != -1:
                    css_link = f'    <link rel="stylesheet" href="{css_filename}">\n'
                    html_content = html_content[:head_end] + css_link + html_content[head_end:]
                    if self.logger:
                        self.logger.info(f"Added CSS reference: {css_filename}")
                else:
                    # If no head end tag found, try to add before body
                    body_start = html_content.find('<body')
                    if body_start != -1:
                        html_content = html_content[:body_start] + f'<head>\n    <link rel="stylesheet" href="{css_filename}">\n</head>\n' + html_content[body_start:]
                        if self.logger:
                            self.logger.info(f"Added head with CSS reference: {css_filename}")
                    else:
                        # Last resort: prepend to the content
                        html_content = f'<!DOCTYPE html>\n<html>\n<head>\n    <link rel="stylesheet" href="{css_filename}">\n</head>\n<body>\n{html_content}\n</body>\n</html>'
                        if self.logger:
                            self.logger.info(f"Restructured HTML and added CSS reference: {css_filename}")
        
        # Fix JS reference if found
        if js_path:
            # Extract just the filename without path
            js_filename = js_path.split('/')[-1]
            
            # Check for existing script tag with src
            has_script_tag = bool(re.search(r'<script[^>]*src=["\'][^"\']*["\'][^>]*>', html_content, re.IGNORECASE))
            
            if has_script_tag:
                # Replace any script reference with the correct filename
                html_content = re.sub(
                    r'<script[^>]*src=["\'][^"\']*["\'][^>]*></script>',
                    f'<script src="{js_filename}" defer></script>',
                    html_content,
                    flags=re.IGNORECASE
                )
                if self.logger:
                    self.logger.info(f"Updated JS reference to: {js_filename}")
            else:
                # Try to add before closing head tag
                head_end = html_content.find('</head>')
                if head_end != -1:
                    script_tag = f'    <script src="{js_filename}" defer></script>\n'
                    html_content = html_content[:head_end] + script_tag + html_content[head_end:]
                    if self.logger:
                        self.logger.info(f"Added JS reference: {js_filename}")
                else:
                    # If no head end tag, try to add before body
                    body_start = html_content.find('<body')
                    if body_start != -1:
                        html_content = html_content[:body_start] + f'<script src="{js_filename}" defer></script>\n' + html_content[body_start:]
                        if self.logger:
                            self.logger.info(f"Added JS reference: {js_filename}")
                    else:
                        # Last resort: add at the end of the content
                        html_content = html_content + f'\n<script src="{js_filename}" defer></script>\n'
                        if self.logger:
                            self.logger.info(f"Added JS reference at end: {js_filename}")
        
        # Ensure we have a complete HTML document structure
        if not html_content.strip().lower().startswith('<!doctype'):
            if not html_content.strip().lower().startswith('<html'):
                html_content = f'<!DOCTYPE html>\n<html>\n{html_content}</html>'
                if self.logger:
                    self.logger.info("Added missing DOCTYPE and html tags")
            else:
                html_content = f'<!DOCTYPE html>\n{html_content}'
                if self.logger:
                    self.logger.info("Added missing DOCTYPE")
                    
        # Ensure <head> comes before <body>
        head_pos = html_content.lower().find('<head')
        body_pos = html_content.lower().find('<body')
        
        if head_pos > body_pos and body_pos != -1 and head_pos != -1:
            # Extract the head content
            head_end = html_content.lower().find('</head>', head_pos)
            head_content = html_content[head_pos:head_end+7]
            
            # Remove the head from its current position
            html_content = html_content[:head_pos] + html_content[head_end+7:]
            
            # Insert it before body
            body_pos = html_content.lower().find('<body')  # Recalculate position
            html_content = html_content[:body_pos] + head_content + html_content[body_pos:]
            if self.logger:
                self.logger.info("Fixed HTML structure: moved head before body")
        
        return html_content
