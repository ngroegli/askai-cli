from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import yaml
import re
import os

class InputType(Enum):
    TEXT = "text"
    NUMBER = "number"
    SELECT = "select"
    FILE = "file"  # For file path or content
    URL = "url"    # For URL validation
    IMAGE_FILE = "image_file"  # For image file handling with -img parameter
    PDF_FILE = "pdf_file"  # For PDF file handling with -pdf parameter

@dataclass
class PatternInput:
    name: str
    description: str
    input_type: InputType
    required: bool = True
    default: Any = None
    options: List[str] = None  # For SELECT type
    min_value: float = None    # For NUMBER type
    max_value: float = None    # For NUMBER type
    alternative_to: str = None  # Name of alternative input (only one of them needs to be provided)
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
            alternative_to=data.get('alternative_to'),
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
            if value not in self.options:
                return False, f"Value must be one of: {', '.join(self.options)}"

        elif self.input_type == InputType.FILE:
            try:
                # Just validate that the file exists and is readable
                with open(value, 'r') as f:
                    f.read(1)  # Try to read one byte to verify access
            except Exception as e:
                return False, f"File error: {str(e)}"
        
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
                    return False, f"File does not appear to be an image. Supported formats: {', '.join(image_extensions)}"
            except Exception as e:
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
            except Exception as e:
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
