"""
CSS writer class for writing CSS content to files.
"""

from .base_writer import BaseWriter


class CssWriter(BaseWriter):
    """CSS writer that handles specialized CSS file writing."""
    
    def write_css(self, content: str, file_path: str) -> bool:
        """Write CSS content to a file with appropriate formatting.
        
        Args:
            content: CSS content to write
            file_path: Path where to write the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure file has .css extension
        if not file_path.lower().endswith('.css'):
            file_path += '.css'
            
        # Add a comment header for better identification
        header = "/*\n * Generated CSS file\n */\n\n"
        formatted_content = header + content.strip()
        
        return self.write(formatted_content, file_path)
