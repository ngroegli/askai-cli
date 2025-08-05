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
    HTML = "html"
    CSS = "css"
    JS = "js"

@dataclass
class PatternOutput:
    name: str
    description: str
    output_type: OutputType
    schema: Optional[Dict[str, Any]] = None  # JSON schema for validation
    example: Optional[str] = None  # Example of the expected output
    format_spec: Optional[Dict[str, Any]] = None  # Additional formatting specifications
    required: bool = True  # Whether this output must be present in the response
    auto_run: bool = False  # Whether CODE outputs should prompt for execution
    write_to_file: Optional[str] = None  # Filename to write this output to (None = don't write to file)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatternOutput':
        """Create a PatternOutput instance from a dictionary."""
        return cls(
            name=data['name'],
            description=data['description'],
            output_type=OutputType(data['type']),
            schema=data.get('schema'),
            example=data.get('example'),
            format_spec=data.get('format_spec'),
            required=data.get('required', True),
            auto_run=data.get('auto_run', False),
            write_to_file=data.get('write_to_file')
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

        # TEXT, CODE, MARKDOWN, HTML, CSS, and JS types accept any string value
        elif self.output_type in (OutputType.TEXT, OutputType.CODE, OutputType.MARKDOWN, 
                                 OutputType.HTML, OutputType.CSS, OutputType.JS):
            if not isinstance(value, str):
                return False, f"{self.output_type.value} output must be a string"

        return True, None

    def should_prompt_for_execution(self) -> bool:
        """Check if this CODE output should prompt for execution."""
        return self.output_type == OutputType.CODE and self.auto_run

    def should_write_to_file(self) -> bool:
        """Check if this output should be written to a file."""
        return self.write_to_file is not None and self.write_to_file.strip() != ""
    
    def get_file_extension(self) -> Optional[str]:
        """Get the expected file extension based on output type."""
        extension_map = {
            OutputType.HTML: ".html",
            OutputType.CSS: ".css", 
            OutputType.JS: ".js",
            OutputType.JSON: ".json",
            OutputType.MARKDOWN: ".md",
            OutputType.CODE: ".txt",  # Default for code, could be language-specific
            OutputType.TEXT: ".txt",
            OutputType.TABLE: ".csv",  # Tables could be CSV
            OutputType.LIST: ".txt"
        }
        return extension_map.get(self.output_type)

    @staticmethod
    def display_execution_warning(command: str, output_name: str) -> None:
        """Display a yellow warning banner before prompting for execution."""
        # ANSI color codes for yellow background with black text
        yellow_bg = '\033[43m'
        black_text = '\033[30m'
        bold = '\033[1m'
        reset = '\033[0m'
        
        warning_text = f"⚠️  SECURITY WARNING: About to execute code from '{output_name}'"
        
        # Calculate the width for the border - use at least 80 characters or the length of the longest line
        max_width = max(len(warning_text), len(f" Command: {command}"), 80)
        border = "=" * max_width
        
        print(f"\n{yellow_bg}{black_text}{bold}")
        print(f" {border} ")
        print(f" {warning_text.ljust(max_width-1)} ")
        
        # Handle long commands by wrapping them properly
        if len(command) > max_width - 10:  # Leave some margin for " Command: "
            print(f" Command: {' ' * (max_width - 10)} ")
            # Split command into chunks that fit within the warning box
            command_prefix = "   "
            available_width = max_width - len(command_prefix) - 1
            
            words = command.split()
            current_line = ""
            
            for word in words:
                # If adding this word would exceed the width, start a new line
                if len(current_line) + len(word) + 1 > available_width:
                    if current_line:  # Only print if we have content
                        print(f"{command_prefix}{current_line.ljust(available_width)} ")
                        current_line = word
                    else:
                        # Single word is too long, print it anyway
                        print(f"{command_prefix}{word.ljust(available_width)} ")
                        current_line = ""
                else:
                    if current_line:
                        current_line += " " + word
                    else:
                        current_line = word
            
            # Print any remaining content
            if current_line:
                print(f"{command_prefix}{current_line.ljust(available_width)} ")
        else:
            print(f" Command: {command.ljust(max_width-10)} ")
        
        print(f" {border} ")
        print(f"{reset}")

    @staticmethod
    def prompt_for_execution(command: str, output_name: str) -> bool:
        """Prompt user if they want to execute the code and return their choice."""
        PatternOutput.display_execution_warning(command, output_name)
        
        while True:
            response = input(f"Execute this command? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
