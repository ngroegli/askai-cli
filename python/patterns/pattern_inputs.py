"""
Pattern input definitions module for the askai-cli.

This module provides the data structures and validation logic for handling
different types of inputs in pattern definitions, including text, numbers,
selections, files, and URLs. It supports input validation and grouping.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import re
import os

class InputType(Enum):
    """
    Enumeration of supported input types for pattern definitions.

    Each input type has specific validation rules and handling logic.
    """
    TEXT = "text"
    NUMBER = "number"
    SELECT = "select"
    FILE = "file"  # For file path or content
    URL = "url"    # For URL validation
    IMAGE_FILE = "image_file"  # For image file handling with -img parameter
    PDF_FILE = "pdf_file"  # For PDF file handling with -pdf parameter

@dataclass
class InputGroup:
    """Represents a group of related inputs where only a subset needs to be provided"""
    name: str
    description: str
    required_inputs: int = 1  # How many inputs from this group must be provided
    input_names: List[str] = field(default_factory=list)  # Names of inputs in this group

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InputGroup':
        """Create an InputGroup instance from a dictionary."""
        return cls(
            name=data['name'],
            description=data.get('description', f"Group {data['name']}"),
            required_inputs=data.get('required_inputs', 1),
            input_names=data.get('input_names', [])
        )

@dataclass
class PatternInput:
    """
    Represents an input parameter for a pattern with validation capabilities.

    Each input has a type, description, and optional validation rules.
    Inputs can be grouped together and validated according to their type.
    """
    name: str
    description: str
    input_type: InputType
    required: bool = True
    default: Any = None
    options: Optional[List[str]] = None  # For SELECT type
    min_value: Optional[float] = None    # For NUMBER type
    max_value: Optional[float] = None    # For NUMBER type
    group: Optional[str] = None  # Name of the input group this input belongs to
    ignore_undefined: bool = False  # Whether to ignore this input if not provided in non-interactive mode

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatternInput':
        """Create a PatternInput instance from a dictionary."""
        return cls(
            name=data['name'],
            description=data['description'],
            input_type=InputType(data['type']),
            required=data.get('required', True),
            default=data.get('default'),
            options=data.get('options'),
            min_value=data.get('min'),
            max_value=data.get('max'),
            group=data.get('group'),
            ignore_undefined=data.get('ignore_undefined', False)
        )

    def validate_value(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate a value for this input."""
        if value is None:
            if self.required:
                return False, f"'{self.name}' is required"
            return True, None

        if self.input_type == InputType.NUMBER:
            try:
                num_value = float(value)
                if self.min_value is not None and num_value < self.min_value:
                    return False, f"Value must be >= {self.min_value}"
                if self.max_value is not None and num_value > self.max_value:
                    return False, f"Value must be <= {self.max_value}"
            except ValueError:
                return False, "Value must be a number"

        elif self.input_type == InputType.SELECT:
            if value not in (self.options or []):
                return False, f"Value must be one of: {', '.join(self.options or [])}"

        elif self.input_type == InputType.FILE:
            try:
                # Just validate that the file exists and is readable
                with open(value, 'r', encoding='utf-8') as f:
                    f.read(1)  # Try to read one byte to verify access
            except FileNotFoundError:
                return False, f"File not found: {value}"
            except PermissionError:
                return False, f"Permission denied when accessing file: {value}"
            except IOError as e:
                return False, f"I/O error when accessing file: {str(e)}"

        elif self.input_type == InputType.IMAGE_FILE:
            try:
                # Validate that the image file exists and is readable
                # Note: Using 'rb' mode for binary files like images
                with open(value, 'rb') as f:
                    f.read(1)  # Try to read one byte to verify access
                # Check if it has an image extension
                image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
                file_ext = os.path.splitext(value)[1].lower()
                if file_ext not in image_extensions:
                    formats = ', '.join(image_extensions)
                    return False, f"File does not appear to be an image. Supported formats: {formats}"
            except FileNotFoundError:
                return False, f"Image file not found: {value}"
            except PermissionError:
                return False, f"Permission denied when accessing image file: {value}"
            except (IOError, OSError) as e:
                return False, f"Image file error: {str(e)}"

        elif self.input_type == InputType.PDF_FILE:
            try:
                # Validate that the PDF file exists and is readable
                # Using 'rb' mode for binary PDF files
                with open(value, 'rb') as f:
                    f.read(1)  # Try to read one byte to verify access
                # Check if it has a PDF extension
                file_ext = os.path.splitext(value)[1].lower()
                if file_ext != '.pdf':
                    return False, "File does not appear to be a PDF. Only .pdf extension is supported."
            except FileNotFoundError:
                return False, f"PDF file not found: {value}"
            except PermissionError:
                return False, f"Permission denied when accessing PDF file: {value}"
            except (IOError, OSError) as e:
                return False, f"PDF file error: {str(e)}"

        elif self.input_type == InputType.URL:
            # Basic URL validation using regex
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)

            if not url_pattern.match(value):
                return False, "Value must be a valid URL (http:// or https://)"

        return True, None
