from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union, ClassVar
import json
import re
import subprocess
from jsonschema import validate, ValidationError
import logging

logger = logging.getLogger(__name__)

class OutputType(Enum):
    """Enum representing different types of outputs."""
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
    """Defines the expected output from a pattern.
    
    This class represents the contract for how an AI should structure its output
    for a specific field in the pattern response.
    """
    # Basic properties
    name: str
    description: str
    output_type: OutputType
    
    # Validation and example data
    schema: Optional[Dict[str, Any]] = None  # JSON schema for validation
    example: Optional[str] = None  # Example of the expected output
    format_spec: Optional[Dict[str, Any]] = None  # Additional formatting specifications
    
    # Behavior flags
    required: bool = True  # Whether this output must be present in the response
    auto_run: bool = False  # Whether CODE outputs should prompt for execution
    write_to_file: Optional[str] = None  # Filename to write this output to (None = don't write to file)
    is_system_field: bool = False  # Whether this is a special system field like result or visual_output
    
    # Internal content storage
    content: Optional[Any] = field(default=None, repr=False)
    
    # File extension mapping (class variable)
    EXTENSION_MAP: ClassVar[Dict[OutputType, str]] = {
        OutputType.HTML: ".html",
        OutputType.CSS: ".css", 
        OutputType.JS: ".js",
        OutputType.JSON: ".json",
        OutputType.MARKDOWN: ".md",
        OutputType.CODE: ".txt",  # Default for code
        OutputType.TEXT: ".txt",
        OutputType.TABLE: ".csv",  # Tables could be CSV
        OutputType.LIST: ".txt"
    }
    
    # Common Linux commands for basic validation
    COMMON_COMMANDS: ClassVar[List[str]] = [
        'ls', 'cd', 'pwd', 'mkdir', 'cp', 'mv', 'rm', 'grep', 
        'find', 'cat', 'echo', 'ps', 'kill', 'df', 'du', 'tar', 
        'chmod', 'chown', 'wget', 'curl'
    ]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatternOutput':
        """Create a PatternOutput instance from a dictionary.
        
        Args:
            data: Dictionary containing output definition
            
        Returns:
            PatternOutput: Instantiated pattern output object
        """
        name = data['name']
        # Mark result and visual_output as special system fields
        is_system_field = name in ["result", "visual_output"]
        
        # Get auto_run value - ensure it's a boolean
        auto_run = bool(data.get('auto_run', False))
        
        # Special case for linux CLI command generation
        if name == "result" and data.get('type') == 'code':
            # Ensure auto_run is set for Linux CLI command generation if specified
            if 'auto_run' in data and data['auto_run'] is True:
                auto_run = True
        
        output_obj = cls(
            name=name,
            description=data['description'],
            output_type=OutputType(data['type']),
            schema=data.get('schema'),
            example=data.get('example'),
            format_spec=data.get('format_spec'),
            required=data.get('required', True),
            auto_run=auto_run,
            write_to_file=data.get('write_to_file'),
            is_system_field=is_system_field
        )
        
        return output_obj

    def validate_value(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate an output value against this output's specifications.
        
        Args:
            value: The value to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if value is None:
            if self.required:
                return False, f"'{self.name}' output is required"
            return True, None

        # Validate based on output type
        if self.output_type == OutputType.JSON and self.schema:
            try:
                # Parse string to JSON if needed
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

        # Text types accept any string value
        elif self.output_type in (OutputType.TEXT, OutputType.CODE, OutputType.MARKDOWN, 
                                 OutputType.HTML, OutputType.CSS, OutputType.JS):
            if not isinstance(value, str):
                return False, f"{self.output_type.value} output must be a string"

        return True, None

    def should_prompt_for_execution(self) -> bool:
        """Check if this output should prompt for execution.
        
        Returns:
            bool: True if execution prompt should be shown
        """
        # Method 1: Code outputs that have auto_run set
        if self.output_type == OutputType.CODE and self.auto_run:
            return True
            
        # Method 2: Special case for "result" field of type CODE
        if self.name == "result" and self.is_system_field and self.output_type == OutputType.CODE:
            return True
        
        # Not executable
        return False

    def should_write_to_file(self) -> bool:
        """Check if this output should be written to a file.
        
        Returns:
            bool: True if output should be written to file
        """
        return self.write_to_file is not None and self.write_to_file.strip() != ""
    
    def get_file_extension(self) -> str:
        """Get the expected file extension based on output type.
        
        Returns:
            str: The file extension including the dot
        """
        return self.EXTENSION_MAP.get(self.output_type, ".txt")
    
    def get_content(self) -> Optional[Any]:
        """Get the content associated with this output.
        
        Returns:
            Any: The output content
        """
        return self.content
    
    def set_content(self, content: Any) -> None:
        """Set the content for this output.
        
        Args:
            content: The content to set
        """
        self.content = content
        
    @staticmethod
    def is_linux_command(text: str) -> bool:
        """Check if a string appears to be a Linux command.
        
        Args:
            text: The text to check
            
        Returns:
            bool: True if the text appears to be a Linux command
        """
        if not isinstance(text, str) or not text.strip():
            return False
        
        # For simple detection, check if the first word is a common command
        command_first_word = text.strip().split()[0] if text.strip() else ""
        if command_first_word in PatternOutput.COMMON_COMMANDS:
            return True
            
        # Default to True for most text in a command context
        return True

    @staticmethod
    def execute_command(command: str, output_name: str = "command") -> bool:
        """Display a warning, prompt for execution, and execute the command if confirmed.
        
        Args:
            command: The command to execute
            output_name: The name of the output field
            
        Returns:
            bool: True if the command was executed successfully
        """
        # Input validation
        if not isinstance(command, str) or not command.strip():
            print("\n❌ Error: Empty or invalid command")
            return False
        
        # Clean up command - remove any markdown formatting
        cleaned_command = PatternOutput._clean_command(command)
        
        # Show warning and prompt for confirmation
        PatternOutput._display_execution_warning(cleaned_command, output_name)
        
        # Get user confirmation
        if not PatternOutput._get_user_confirmation():
            print("\n⏭️ Command execution skipped")
            return False
        
        # Execute the command
        print("\n📄 Executing command...\n")
        try:
            subprocess.run(cleaned_command, shell=True)
            print("\n✅ Command executed successfully")
            return True
        except Exception as e:
            print(f"\n❌ Error executing command: {str(e)}")
            return False
    
    @staticmethod
    def _clean_command(command: str) -> str:
        """Clean a command string, removing markdown formatting.
        
        Args:
            command: Raw command string
            
        Returns:
            str: Cleaned command string
        """
        # Handle markdown code blocks
        if command.startswith("```") and "\n" in command:
            lines = command.split("\n")
            start_idx = 1  # Skip the opening ```
            end_idx = len(lines) - 1
            
            # Find the closing ```
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "```":
                    end_idx = i
                    break
                    
            # Extract the command lines
            command_lines = lines[start_idx:end_idx]
            return "\n".join(command_lines).strip()
        
        return command.strip()
    
    @staticmethod
    def _display_execution_warning(command: str, output_name: str) -> None:
        """Display a warning banner before prompting for execution.
        
        Args:
            command: The command to execute
            output_name: The name of the output field
        """
        border = "=" * 80
        
        print("\n" + border)
        print(f"⚠️  SECURITY WARNING: About to execute command from '{output_name}'")
        print(f"Command: {command}")
        print(border)
    
    @staticmethod
    def _get_user_confirmation() -> bool:
        """Get user confirmation for command execution.
        
        Returns:
            bool: True if user confirmed execution
        """
        try:
            print("\nExecute this command? (y/n): ", end="", flush=True)
            try:
                # Try to use the Python built-in input function
                import builtins
                response = builtins.input()
            except Exception:
                # Fall back to readline if input fails
                import sys
                sys.stdout.flush()
                response = sys.stdin.readline().strip()
                
            response = response.strip().lower() if response else "n"
            return response in ['y', 'yes']
            
        except Exception as e:
            logger.error(f"Error during input handling: {str(e)}")
            return False
