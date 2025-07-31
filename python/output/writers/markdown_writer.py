"""
Markdown writer class for writing Markdown content to files.
"""

import os
import re
from typing import Optional, List, Dict

from .base_writer import BaseWriter


class MarkdownWriter(BaseWriter):
    """Markdown writer that handles Markdown file writing with proper formatting."""
    
    def __init__(self, output_dir: Optional[str] = None, logger=None):
        """Initialize the Markdown writer.
        
        Args:
            output_dir: Optional output directory for markdown files
            logger: Optional logger instance
        """
        super().__init__(logger=logger)
        self.output_dir = output_dir
    
    def write(self, content: str, filename: str = "output.md", front_matter: Optional[Dict] = None) -> str:
        """Write Markdown content to a file with optional front matter.
        
        Args:
            content: Markdown content to write
            filename: Name of the file to write
            front_matter: Optional YAML front matter to include
            
        Returns:
            str: Path to the written file
        """
        # Ensure file has .md extension
        if not filename.lower().endswith('.md'):
            filename += '.md'
        
        # Determine file path
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
            file_path = os.path.join(self.output_dir, filename)
        else:
            file_path = filename
        
        # Format the markdown content
        formatted_content = self._format_markdown(content, front_matter)
        
        # Write the file
        super().write(formatted_content, file_path)
        
        return file_path
        
    def write_markdown(self, content: str, file_path: str, front_matter: Optional[Dict] = None) -> bool:
        """Write Markdown content to a file with optional front matter (legacy method).
        
        Args:
            content: Markdown content to write
            file_path: Path where to write the file
            front_matter: Optional YAML front matter to include
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure file has .md extension
        if not file_path.lower().endswith('.md'):
            file_path += '.md'
        
        # Format the markdown content
        formatted_content = self._format_markdown(content, front_matter)
        
        return super().write(formatted_content, file_path)
    
    def _format_markdown(self, markdown_content: str, front_matter: Optional[Dict] = None) -> str:
        """Format Markdown content for proper output.
        
        Args:
            markdown_content: The Markdown content to format
            front_matter: Optional YAML front matter to include
            
        Returns:
            str: Formatted Markdown content
        """
        # Remove markdown code block markers if present
        markdown_content = re.sub(r'^```md\s*|^```markdown\s*', '', markdown_content)
        markdown_content = re.sub(r'\s*```$', '', markdown_content)
        
        # Ensure the content starts with a title if not present
        if not re.match(r'^#\s+', markdown_content):
            # Try to extract a title from the first paragraph or line
            lines = markdown_content.split('\n')
            first_line = next((line for line in lines if line.strip()), "Document")
            
            # Remove any markdown formatting from the first line
            title = re.sub(r'[*_`#]', '', first_line).strip()
            
            # Limit title length
            if len(title) > 50:
                title = title[:47] + "..."
            
            # Add the title as H1
            markdown_content = f"# {title}\n\n{markdown_content}"
            
            if self.logger:
                self.logger.info(f"Added missing title to markdown: '{title}'")
        
        # Add front matter if provided
        if front_matter and isinstance(front_matter, dict):
            # Convert front matter to YAML format
            yaml_front_matter = "---\n"
            for key, value in front_matter.items():
                if isinstance(value, list):
                    yaml_front_matter += f"{key}:\n"
                    for item in value:
                        yaml_front_matter += f"  - {item}\n"
                else:
                    yaml_front_matter += f"{key}: {value}\n"
            yaml_front_matter += "---\n\n"
            
            # Check if the markdown already has front matter
            if not re.match(r'^---\s*\n', markdown_content):
                markdown_content = yaml_front_matter + markdown_content
                if self.logger:
                    self.logger.info("Added YAML front matter to markdown")
        
        # Ensure there's a blank line at the end of the file
        if not markdown_content.endswith('\n\n'):
            if markdown_content.endswith('\n'):
                markdown_content += '\n'
            else:
                markdown_content += '\n\n'
        
        return markdown_content
