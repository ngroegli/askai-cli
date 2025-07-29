from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import json
from jsonschema import validate, ValidationError

class OutputType(Enum):
    TEXT = "text"
    JSON = "json"
    TABLE = "table"
    LIST = "list"
    CODE = "code"
    MARKDOWN = "markdown"

@dataclass
class SystemOutput:
    name: str
    description: str
    output_type: OutputType
    schema: Optional[Dict[str, Any]] = None  # JSON schema for validation
    example: Optional[str] = None  # Example of the expected output
    format_spec: Optional[Dict[str, Any]] = None  # Additional formatting specifications
    required: bool = True  # Whether this output must be present in the response

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemOutput':
        """Create a SystemOutput instance from a dictionary."""
        return cls(
            name=data['name'],
            description=data['description'],
            output_type=OutputType(data['type']),
            schema=data.get('schema'),
            example=data.get('example'),
            format_spec=data.get('format_spec'),
            required=data.get('required', True)
        )

    def validate_value(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate an output value against this output's specifications."""
        if value is None:
            if self.required:
                return False, f"'{self.name}' output is required"
            return True, None

        if self.output_type == OutputType.JSON and self.schema:
            try:
                # If value is a string, try to parse it as JSON
                if isinstance(value, str):
                    value = json.loads(value)
                validate(instance=value, schema=self.schema)
            except ValidationError as e:
                return False, f"JSON validation error: {str(e)}"
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON: {str(e)}"

        elif self.output_type == OutputType.TABLE:
            if not isinstance(value, (list, tuple)) or not all(isinstance(row, (list, tuple)) for row in value):
                return False, "Table output must be a list of lists"

        elif self.output_type == OutputType.LIST:
            if not isinstance(value, (list, tuple)):
                return False, "List output must be a list or tuple"

        # TEXT, CODE, and MARKDOWN types accept any string value
        elif self.output_type in (OutputType.TEXT, OutputType.CODE, OutputType.MARKDOWN):
            if not isinstance(value, str):
                return False, f"{self.output_type.value} output must be a string"

        return True, None
