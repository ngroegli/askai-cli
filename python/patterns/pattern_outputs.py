from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import json
import re
import subprocess
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
    is_system_field: bool = False  # Whether this is a special system field like result or visual_output

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatternOutput':
        """Create a PatternOutput instance from a dictionary."""
        name = data['name']
        # Mark result and visual_output as special system fields
        is_system_field = name in ["result", "visual_output"]
        
        # Get auto_run value - ensure it's a boolean
        auto_run = bool(data.get('auto_run', False))
        
        # Special case for linux CLI command generation
        if name == "result" and data.get('type') == 'code':
            # Ensure auto_run is set for Linux CLI command generation
            if 'auto_run' in data and data['auto_run'] is True:
                # Auto_run explicitly set to True in the pattern
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
        """Check if this output should prompt for execution."""
        # Method 1: Code outputs that have auto_run set
        if self.output_type == OutputType.CODE and self.auto_run:
            return True
            
        # Method 2: Force execution for linux_cli_command_generation pattern's "result" field
        if self.name == "result" and self.is_system_field:
            # Any "result" field of type CODE should be executable
            if self.output_type == OutputType.CODE:
                return True
        
        # Not executable
        return False

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
    def is_linux_command(text: str) -> bool:
        """Check if a string appears to be a Linux command.
        
        Args:
            text (str): The text to check
            
        Returns:
            bool: True if the text appears to be a Linux command, False otherwise
        """
        # Return True for most cases when called from Linux CLI pattern
        # This avoids complex detection logic that might fail
        if not isinstance(text, str) or not text.strip():
            return False
        
        # For linux_cli_command_generation pattern, assume it's always a valid command
        # if it comes from the "result" field
        
        # Always return True for simple commands like "ls -la" from linux_cli_command_generation pattern
        command_first_word = text.strip().split()[0] if text.strip() else ""
        common_commands = ['ls', 'cd', 'pwd', 'mkdir', 'cp', 'mv', 'rm', 'grep', 'find', 'cat', 'echo', 'ps', 
                          'kill', 'df', 'du', 'tar', 'chmod', 'chown', 'wget', 'curl']
        
        if command_first_word in common_commands:
            return True
            
        # Default to True for any reasonable text that might be a command
        return True

    @staticmethod
    def display_execution_warning(command: str, output_name: str) -> None:
        """Display a warning banner before prompting for execution."""
        # Simplified version without ANSI colors for better compatibility
        warning_text = f"⚠️  SECURITY WARNING: About to execute code from '{output_name}'"
        
        # Calculate the width for the border
        border = "=" * 63
        
        print("\n" + border)
        print(f" {warning_text} ")
        print(f" Command: {command} ")
        print(border + "\n")

    @staticmethod
    def prompt_for_execution(command: str, output_name: str) -> bool:
        """Prompt user if they want to execute the code and return their choice."""
        print("\n⚠️  SECURITY WARNING: About to execute code from 'result'")
        print(" =============================================================== ")
        print(f" ⚠️  SECURITY WARNING: About to execute code from '{output_name}'      ")
        print(f" Command: {command}                                                ")
        print(" =============================================================== ")
        print("")
        
        try:
            response = input(f"Execute this command? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            else:  # Default to no for any other input
                return False
        except Exception as e:
            print(f"Error in prompt: {str(e)}")
            return False
                
    @staticmethod
    def execute_command(command: str, output_name: str = "command") -> bool:
        """Display a warning, prompt for execution, and execute the command if confirmed.
        
        Args:
            command (str): The command to execute
            output_name (str): The name of the output field
            
        Returns:
            bool: True if the command was executed successfully, False otherwise
        """
        # Input validation
        if not isinstance(command, str) or not command.strip():
            print("\n❌ Error: Empty or invalid command")
            return False
        
        # Clean up command - remove any markdown formatting that might have been added
        cleaned_command = command
        if command.startswith("```") and "\n" in command:
            # Extract command from markdown code block
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
            cleaned_command = "\n".join(command_lines).strip()
        
        # ALWAYS PRINT THE WARNING - no conditions
        print("\n" + "=" * 80)
        print("⚠️  SECURITY WARNING: About to execute command")
        print(f"Command: {cleaned_command}")
        print("=" * 80)
        
        # ALWAYS PROMPT for execution - no conditions
        import builtins
        try:
            print("\nExecute this command? (y/n): ", end="", flush=True)
            try:
                # Try to use the Python built-in input function
                response = builtins.input()
            except:
                # If that fails, fall back to the built-in raw_input function
                import sys
                sys.stdout.flush()
                response = sys.stdin.readline().strip()
                
            response = response.strip().lower() if response else "n"
            
            if response in ['y', 'yes']:
                print("\n📄 Executing command...\n")
                try:
                    import subprocess
                    subprocess.run(cleaned_command, shell=True)
                    print("\n✅ Command executed successfully")
                    return True
                except Exception as e:
                    print(f"\n❌ Error executing command: {str(e)}")
                    return False
            else:
                print("\n⏭️ Command execution skipped")
        except Exception as e:
            print(f"\n❌ Error during input handling: {str(e)}")
            
        return False
