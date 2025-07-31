"""
Base writer class for writing content to files.
"""

import os
from pathlib import Path
from typing import Optional


class BaseWriter:
    """Base class for writing content to files."""
    
    def __init__(self, logger=None):
        """Initialize the writer.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger
    
    def write(self, content: str, file_path: str) -> bool:
        """Write content to a file.
        
        Args:
            content: Content to write
            file_path: Path where to write the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure parent directory exists
            path_obj = Path(file_path)
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            if self.logger:
                self.logger.info(f"Content written to {file_path} ({len(content)} chars)")
            
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error writing to {file_path}: {str(e)}")
            return False
    
    def get_output_directory(self, suggested_path: Optional[str] = None) -> Optional[str]:
        """Get the directory where files should be written, with user interaction.
        
        Args:
            suggested_path: Optional suggested path to use
            
        Returns:
            str: Directory path, or None if user cancelled
        """
        print("\n📁 File Output Location")
        print("=" * 50)
        print("The system will create files automatically.")
        print("Hint: Use '.' for current directory or specify a path like './my-website'")
        
        if suggested_path:
            print(f"Suggested path: {suggested_path}")
            
        print("Press Enter for current directory (.) or specify a path:")
        
        try:
            directory = input("Enter directory path (or 'cancel' to skip file creation): ").strip()
        except (KeyboardInterrupt, EOFError):
            return None
        
        if directory.lower() == 'cancel':
            return None
        
        # Default to current directory if empty
        if not directory:
            directory = "."
        
        # Expand relative paths
        directory = os.path.expanduser(directory)
        directory_path = Path(directory)
        
        # Check if directory exists
        if directory_path.exists():
            if directory_path.is_dir():
                return str(directory_path.resolve())
            else:
                print(f"❌ '{directory}' exists but is not a directory. Using current directory instead.")
                return str(Path(".").resolve())
        else:
            # Directory doesn't exist, ask to create
            print(f"📂 Directory '{directory}' does not exist.")
            try:
                create = input("Create this directory? (y/n): ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                return str(Path(".").resolve())
            
            if create in ['y', 'yes', '']:  # Default to yes if empty
                try:
                    directory_path.mkdir(parents=True, exist_ok=True)
                    print(f"✅ Created directory: {directory_path.resolve()}")
                    return str(directory_path.resolve())
                except Exception as e:
                    print(f"❌ Error creating directory: {str(e)}")
                    print("Using current directory instead.")
                    return str(Path(".").resolve())
            else:
                print("Using current directory instead.")
                return str(Path(".").resolve())
