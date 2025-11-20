"""Directory management for output operations.

This module handles output directory creation, validation, and management.
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class DirectoryManager:
    """Manages output directories and file paths."""

    def __init__(self, base_output_dir: Optional[str] = None):
        """Initialize directory manager.

        Args:
            base_output_dir: Base output directory to use
        """
        self.base_output_dir = base_output_dir

    def get_output_directory(self) -> Optional[str]:
        """Get output directory with user confirmation if needed.

        Returns:
            Optional[str]: Output directory path or None if cancelled
        """
        # Use configured directory if available
        if self.base_output_dir:
            return self.base_output_dir

        # Prompt user for directory
        print("\n📁 File Output Location")
        print("=" * 50)
        print("The system will create files automatically.")
        print("Hint: Use '.' for current directory or specify a path like './my-website'")

        try:
            directory = input("Enter directory path (or 'cancel' to skip file creation): ").strip()

            if directory.lower() == 'cancel':
                return None

            # Default to current directory
            if not directory:
                directory = "."

            # Resolve path
            directory_path = Path(os.path.expanduser(directory))

            # Check if directory exists
            if directory_path.exists():
                if directory_path.is_dir():
                    return str(directory_path.resolve())
                print(f"❌ '{directory}' exists but is not a directory. Using current directory instead.")
                return str(Path(".").resolve())

            # Confirm directory creation
            print(f"📂 Directory '{directory}' does not exist.")
            create = input("Create this directory? (y/n): ").strip().lower()
            if create in ['y', 'yes', '']:
                os.makedirs(directory_path, exist_ok=True)
                return str(directory_path.resolve())

            print("Using current directory instead.")
            return str(Path(".").resolve())

        except (KeyboardInterrupt, EOFError) as e:
            logger.warning("Input interrupted: %s", str(e))
            print("\nUsing current directory for output.")
            return str(Path(".").resolve())

    def ensure_directory_exists(self, directory: str) -> bool:
        """Ensure a directory exists, creating it if necessary.

        Args:
            directory: Directory path to ensure exists

        Returns:
            True if directory exists or was created successfully
        """
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error("Failed to create directory %s: %s", directory, str(e))
            return False

    def validate_output_path(self, output_path: str) -> bool:
        """Validate an output path for security and accessibility.

        Args:
            output_path: Path to validate

        Returns:
            True if path is valid and safe
        """
        try:
            # Resolve the path to check for directory traversal
            resolved_path = Path(output_path).resolve()

            # Check for directory traversal attempts
            if ".." in str(output_path):
                logger.warning("Directory traversal attempt detected: %s", output_path)
                return False

            # Check if parent directory is accessible
            parent_dir = resolved_path.parent
            if not parent_dir.exists():
                # Try to create it
                return self.ensure_directory_exists(str(parent_dir))

            return True

        except Exception as e:
            logger.error("Error validating output path %s: %s", output_path, str(e))
            return False
