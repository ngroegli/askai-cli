import os
import sys
import json
import yaml
from typing import List, Dict, Any, Optional, Union
from .pattern_inputs import PatternInput, InputType
from .pattern_outputs import PatternOutput
from .pattern_configuration import (
    PatternConfiguration,
    ModelConfiguration,
    PatternPurpose,
    PatternFunctionality
)
from utils import print_error_or_warnings

class PatternManager:
    def __init__(self, base_path: str):
        """Initialize the pattern manager.
        
        Args:
            base_path: Base path of the application
        """
        self.patterns_dir = os.path.join(base_path, "patterns")
        if not os.path.isdir(self.patterns_dir):
            raise ValueError(f"No 'patterns' directory found at {self.patterns_dir}")

    def list_patterns(self) -> List[Dict[str, Any]]:
        """List all available pattern files.
        
        Returns:
            List[Dict[str, Any]]: List of pattern metadata
        """
        patterns = []
        for filename in os.listdir(self.patterns_dir):
            if filename.endswith('.md') and not filename.startswith('_'):
                file_path = os.path.join(self.patterns_dir, filename)
                pattern_id = filename.removesuffix('.md')
                
                # Read first line of the file to get the pattern name
                with open(file_path, 'r') as f:
                    first_line = f.readline().strip()
                    name = first_line.replace('# Pattern:', '').strip()
                
                patterns.append({
                    'pattern_id': pattern_id,
                    'name': name,
                    'file_path': file_path
                })
        
        return sorted(patterns, key=lambda x: x['name'])

    def _parse_pattern_inputs(self, content: str) -> List[PatternInput]:
        """Parse pattern inputs from markdown content.
        
        Args:
            content: The markdown content to parse
            
        Returns:
            List[PatternInput]: List of parsed pattern inputs
        """
        # Find the Pattern Inputs section
        if "## Pattern Inputs" not in content:
            return []
            
        try:
            # Extract the yaml block
            yaml_text = content.split("## Pattern Inputs")[1]
            yaml_block = yaml_text.split("```yaml")[1].split("```")[0]
            
            # Parse the yaml
            inputs_data = yaml.safe_load(yaml_block)
            
            # Convert to PatternInput objects
            return [PatternInput.from_dict(input_data) for input_data in inputs_data.get('inputs', [])]
        except Exception as e:
            print_error_or_warnings(f"Error parsing pattern inputs: {str(e)}")
            return []

    def _parse_pattern_outputs(self, content: str) -> List[PatternOutput]:
        """Parse pattern outputs from markdown content.
        
        Args:
            content: The markdown content to parse
            
        Returns:
            List[PatternOutput]: List of parsed pattern outputs
        """
        if "## Pattern Outputs" not in content:
            return []
            
        try:
            yaml_text = content.split("## Pattern Outputs")[1]
            yaml_block = yaml_text.split("```yaml")[1].split("```")[0]
            outputs_data = yaml.safe_load(yaml_block)
            return [PatternOutput.from_dict(output_data) for output_data in outputs_data.get('outputs', [])]
        except Exception as e:
            print_error_or_warnings(f"Error parsing pattern outputs: {str(e)}")
            return []

    def _parse_pattern_purpose(self, content: str) -> Optional[PatternPurpose]:
        """Parse pattern purpose from markdown content.
        
        Args:
            content: The markdown content to parse
            
        Returns:
            Optional[PatternPurpose]: Parsed pattern purpose
        """
        try:
            # Extract name from the first line
            name = content.split('\n')[0].replace('# Pattern:', '').strip()
            
            # Extract description from the Purpose section
            description = ""
            if "## Purpose" in content:
                purpose_text = content.split("## Purpose")[1].split("##")[0].strip()
                description = purpose_text

            return PatternPurpose.from_text(name, description)
        except Exception as e:
            print_error_or_warnings(f"Error parsing pattern purpose: {str(e)}")
            return None

    def _parse_pattern_functionality(self, content: str) -> Optional[PatternFunctionality]:
        """Parse pattern functionality from markdown content.
        
        Args:
            content: The markdown content to parse
            
        Returns:
            Optional[PatternFunctionality]: Parsed pattern functionality
        """
        try:
            if "## Functionality" in content:
                functionality_text = content.split("## Functionality")[1].split("##")[0].strip()
                return PatternFunctionality.from_text(functionality_text)
            return None
        except Exception as e:
            print_error_or_warnings(f"Error parsing pattern functionality: {str(e)}")
            return None

    def _parse_model_configuration(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse model configuration from markdown content.
        
        Args:
            content: The markdown content to parse
            
        Returns:
            Optional[Dict[str, Any]]: Parsed model configuration data
        """
        if "## Model Configuration" not in content and "## Model Configuration:" not in content:
            return None
            
        try:
            # Find the model configuration section
            parts = content.split("## Model Configuration")
            if len(parts) < 2:
                parts = content.split("## Model Configuration:")
            if len(parts) < 2:
                return None
                
            config_section = parts[1]
            
            # Split into lines and look for the YAML block
            lines = config_section.split('\n')
            yaml_lines = []
            in_yaml_block = False
            
            for line in lines:
                stripped = line.strip()
                if stripped == '```yaml':
                    in_yaml_block = True
                    continue
                elif stripped == '```':
                    if in_yaml_block:  # Only break if we were in a YAML block
                        break
                elif in_yaml_block:
                    yaml_lines.append(line)
            
            if not yaml_lines:
                return None
            
            # Join the YAML lines and parse
            yaml_content = '\n'.join(yaml_lines)
            
            # Parse the YAML content
            config_data = yaml.safe_load(yaml_content)
            
            # Get just the model configuration part
            if isinstance(config_data, dict) and 'model' in config_data:
                return {'model': config_data['model']}
                
            return None
        except Exception as e:
            print_error_or_warnings(f"Error parsing model configuration: {str(e)}")
            return None

    def _parse_pattern_configuration(self, content: str) -> Optional[PatternConfiguration]:
        """Parse complete pattern configuration from markdown content.
        
        Args:
            content: The markdown content to parse
            
        Returns:
            Optional[PatternConfiguration]: Parsed pattern configuration
        """
        try:
            # Parse individual components
            purpose = self._parse_pattern_purpose(content)
            if not purpose:
                print("[DEBUG] Failed to parse pattern purpose.")
            functionality = self._parse_pattern_functionality(content)
            if not functionality:
                print("[DEBUG] Failed to parse pattern functionality.")
            model_config = self._parse_model_configuration(content)
            if not model_config:
                print("[DEBUG] No model configuration found or failed to parse (this is OK if model is optional).")
            # Extract format instructions if present
            format_instructions = None
            if "format_instructions:" in content:
                format_section = content.split("format_instructions: |")[1].split("\n")
                format_instructions = "\n".join(line for line in format_section 
                                             if not line.strip().startswith("##") 
                                             and not line.strip().startswith("```"))

            # Create complete configuration
            if purpose and functionality:
                return PatternConfiguration.from_components(
                    purpose=purpose,
                    functionality=functionality,
                    model_config=model_config,
                    format_instructions=format_instructions
                )
            print("[DEBUG] Pattern configuration missing required sections (purpose or functionality). Returning None.")
            return None
        except Exception as e:
            print_error_or_warnings(f"Error creating pattern configuration: {str(e)}")
            return None

    def _parse_pattern_prompt(self, content: str) -> str:
        """Extract just the purpose and functionality sections for the prompt.
        
        Args:
            content: The full markdown content
            
        Returns:
            str: The purpose and functionality sections only
        """
        sections = []
        
        # Get purpose section
        if "## Purpose" in content:
            purpose = content.split("## Purpose")[1].split("##")[0].strip()
            sections.append("## Purpose\n\n" + purpose)
            
        # Get functionality section
        if "## Functionality" in content:
            functionality = content.split("## Functionality")[1].split("##")[0].strip()
            sections.append("## Functionality\n\n" + functionality)
            
        return "\n\n".join(sections)

    def get_pattern_content(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get the content and metadata of a specific pattern file.
        
        Args:
            pattern_id: The pattern identifier (filename without .md)
            
        Returns:
            Optional[Dict[str, Any]]: Dictionary containing pattern content and metadata
        """
        file_path = os.path.join(self.patterns_dir, f"{pattern_id}.md")
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r') as f:
            content = f.read()
        return {
            'prompt_content': self._parse_pattern_prompt(content),
            'inputs': self._parse_pattern_inputs(content),
            'outputs': self._parse_pattern_outputs(content),
            'configuration': self._parse_pattern_configuration(content)
        }

    def _read_input_file(self, file_path: str) -> Optional[str]:
        """Read content from an input file.
        
        Args:
            file_path: Path to the input file
            
        Returns:
            Optional[str]: File content or None if file cannot be read
        """
        try:
            with open(file_path, 'r') as f:
                return f.read().strip()
        except Exception as e:
            print_error_or_warnings(f"Error reading input file '{file_path}': {str(e)}")
            return None

    def process_pattern_inputs(self, pattern_id: str, 
                            input_values: Optional[Dict[str, Any]] = None,
                            interactive: bool = True) -> Optional[Dict[str, Any]]:
        """Process pattern inputs from JSON values or interactive input.
        
        Args:
            pattern_id: The pattern identifier
            input_values: Optional dictionary of input values (from -pi/--pattern-input)
            interactive: Whether to prompt for missing values
            
        Returns:
            Optional[Dict[str, Any]]: Processed input values or None if validation fails
        """
        pattern_data = self.get_pattern_content(pattern_id)
        if pattern_data is None:
            print_error_or_warnings(f"Pattern '{pattern_id}' does not exist")
            return None
            
        inputs = pattern_data['inputs']
        if not inputs:
            return {}  # No inputs required
            
        # Create input dictionary for quick lookups
        input_dict = {input_def.name: input_def for input_def in inputs}
        result = {}
        
        # Start with provided JSON values
        if input_values:
            result.update(input_values)
            
        # Handle missing values
        i = 0
        while i < len(inputs):
            input_def = inputs[i]
            
            if input_def.name in result:
                i += 1
                continue
                
            # Handle non-interactive mode and ignored undefined inputs
            if not interactive or (not input_def.required and input_def.ignore_undefined):
                if input_def.required and not input_def.ignore_undefined:
                    print_error_or_warnings(f"Required input '{input_def.name}' is missing")
                    return None
                # Set default value for non-required inputs that can be ignored
                if not input_def.required and input_def.ignore_undefined:
                    result[input_def.name] = input_def.default
                i += 1
                continue
                    
            # Interactive input
            while True:
                print(f"\n{input_def.description}")
                if input_def.input_type == InputType.SELECT:
                    print("Options:", ", ".join(input_def.options))
                
                # Show skip option if there's an alternative
                if input_def.alternative_to and input_def.alternative_to not in result:
                    alt_input = input_dict[input_def.alternative_to]
                    print(f"(Press 's' to skip to {alt_input.name} instead)")
                elif not input_def.required:
                    print("(Optional - press Enter to skip)")
                
                value = input(f"{input_def.name}: ").strip()
                
                if value.lower() == 's' and input_def.alternative_to:
                    # Switch to the alternative input
                    alt_name = input_def.alternative_to
                    alt_index = next((idx for idx, inp in enumerate(inputs) if inp.name == alt_name), -1)
                    if alt_index >= 0:
                        i = alt_index  # Move to the alternative input
                        break
                
                if not value:
                    if not input_def.required:
                        result[input_def.name] = input_def.default
                        i += 1
                        break
                    continue
                    
                # Validate the input value
                valid, error = input_def.validate_value(value)
                if not valid:
                    print_error_or_warnings(f"{error}")
                    continue

                # For FILE type inputs, read the file content after validation
                if input_def.input_type == InputType.FILE:
                    content = self._read_input_file(value)
                    if content is None:
                        continue
                    result[input_def.name] = content
                else:
                    result[input_def.name] = value
                
                i += 1
                break
        
        # Validate alternative requirements
        validated_alternatives = set()  # Track which alternative pairs we've validated
        
        for input_def in inputs:
            # Skip if we already validated this pair
            if input_def.name in validated_alternatives:
                continue
                
            # Check if this input is part of an alternative pair
            alt_name = input_def.alternative_to
            if not alt_name:
                continue
                
            # Get the alternative input definition
            alt_input = input_dict.get(alt_name)
            if not alt_input:
                print_error_or_warnings(f"Alternative input '{alt_name}' not found", warning_only=True)
                continue
                
            # Verify bidirectional alternative relationship
            if alt_input.alternative_to != input_def.name:
                print_error_or_warnings(f"Alternative relationship between '{input_def.name}' and '{alt_name}' is not bidirectional", warning_only=True)
                continue
                
            # Check if at least one of the alternatives is provided
            if input_def.required and alt_input.required:
                if input_def.name not in result and alt_name not in result:
                    print_error_or_warnings(f"Either '{input_def.name}' or '{alt_name}' must be provided")
                    return None
                    
            # Mark both inputs as validated
            validated_alternatives.add(input_def.name)
            validated_alternatives.add(alt_name)
                    
        return result

    def display_pattern(self, pattern_id: str) -> None:
        """Display the content of a pattern file.
        
        Args:
            pattern_id: The pattern identifier
        """
        content = self.get_pattern_content(pattern_id)
        if content is None:
            raise ValueError(f"Pattern '{pattern_id}' does not exist")
        print(content)

    def select_pattern(self) -> Optional[str]:
        """Display an interactive pattern selection menu.
        
        Returns:
            Optional[str]: Selected pattern ID or None if selection cancelled
        """
        patterns = self.list_patterns()
        
        if not patterns:
            print("No pattern files found.")
            return None
            
        print("\nAvailable patterns:")
        print("-" * 60)
        
        # Display patterns with index
        for i, pattern in enumerate(patterns, 1):
            print(f"{i}. {pattern['name']}")
            print(f"   ID: {pattern['pattern_id']}")
            print("-" * 60)
        
        print("\nOptions:")
        print("1-{0}. Select pattern".format(len(patterns)))
        print("q. Quit")
        
        while True:
            choice = input(f"\nEnter your choice (1-{len(patterns)} or q): ").lower()
            
            if choice == 'q':
                return None
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(patterns):
                    return patterns[choice_num - 1]['pattern_id']
                else:
                    print(f"Please enter a number between 1 and {len(patterns)}")
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
