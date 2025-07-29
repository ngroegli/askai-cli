from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import yaml

class InputType(Enum):
    TEXT = "text"
    NUMBER = "number"
    SELECT = "select"
    FILE = "file"  # For file path or content

@dataclass
class SystemInput:
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
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemInput':
        """Create a SystemInput instance from a dictionary."""
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

        return True, None
