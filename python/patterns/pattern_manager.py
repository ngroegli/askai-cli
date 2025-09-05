"""
Pattern manager module for the askai-cli.

This module handles the loading, parsing, and processing of pattern files,
which define input requirements, output formats, and execution configurations
for AI interactions. It supports extracting structured data from markdown files
and managing the validation and collection of pattern inputs.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
import yaml
from utils import print_error_or_warnings
from patterns.pattern_inputs import PatternInput, InputGroup, InputType
from patterns.pattern_outputs import PatternOutput
from patterns.pattern_configuration import (
    PatternConfiguration,
    PatternFunctionality,
    PatternPurpose
)

logger = logging.getLogger(__name__)

class PatternManager:
    """
    Manages the loading, validation, and processing of pattern files.

    This class provides functionality to work with pattern definitions stored in markdown files,
    including listing available patterns, loading pattern details, validating inputs against
    pattern requirements, and collecting user inputs for pattern execution.
    """

    def __init__(self, base_path: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the pattern manager.

        Args:
            base_path: Base path of the application
            config: Application configuration dictionary
        """
        # Built-in patterns directory
        self.patterns_dir = os.path.join(base_path, "patterns")
        if not os.path.isdir(self.patterns_dir):
            raise ValueError(f"No 'patterns' directory found at {self.patterns_dir}")

        # Private patterns directory (optional)
        self.private_patterns_dir = None
        if config and 'patterns' in config and 'private_patterns_path' in config['patterns']:
            private_path = config['patterns']['private_patterns_path']
            if private_path and private_path.strip():  # Check for non-empty string
                # Expand user home directory if needed
                expanded_path = os.path.expanduser(private_path.strip())
                if os.path.isdir(expanded_path):
                    self.private_patterns_dir = expanded_path
                    logger.info("Using private patterns directory: %s", expanded_path)
                else:
                    # Ask user if they want to create the directory
                    print(f"\nWarning: Private patterns directory does not exist: {expanded_path}")
                    create_dir = input(f"Would you like to create the directory '{expanded_path}'? (y/n): ").lower().strip()
                    if create_dir == 'y':
                        try:
                            os.makedirs(expanded_path, exist_ok=True)
                            self.private_patterns_dir = expanded_path
                            print(f"Created private patterns directory: {expanded_path}")
                            logger.info("Created private patterns directory: %s", expanded_path)
                        except Exception as e:
                            print(f"Error creating directory '{expanded_path}': {str(e)}")
                            logger.error("Error creating private patterns directory %s: %s", expanded_path, str(e))
                    else:
                        print("Continuing without private patterns directory.")
                        logger.warning("Private patterns directory not created: %s", expanded_path)

    def _get_pattern_directories(self) -> List[str]:
        """Get all pattern directories to search.

        Returns:
            List[str]: List of directories to search for patterns (private first, then built-in)
        """
        directories = []
        # Private patterns come first (higher priority)
        if self.private_patterns_dir:
            directories.append(self.private_patterns_dir)
        # Built-in patterns directory
        directories.append(self.patterns_dir)
        return directories

    def list_patterns(self) -> List[Dict[str, Any]]:
        """List all available pattern files from all directories.

        Returns:
            List[Dict[str, Any]]: List of pattern metadata
        """
        patterns = []
        seen_pattern_ids = set()

        # Search all directories (private patterns first for priority)
        for patterns_dir in self._get_pattern_directories():
            if not os.path.exists(patterns_dir):
                continue

            for filename in os.listdir(patterns_dir):
                if filename.endswith('.md') and not filename.startswith('_'):
                    pattern_id = filename.removesuffix('.md')

                    # Skip if we've already seen this pattern (private overrides built-in)
                    if pattern_id in seen_pattern_ids:
                        continue

                    file_path = os.path.join(patterns_dir, filename)

                    try:
                        # Read first line of the file to get the pattern name
                        with open(file_path, 'r', encoding='utf-8') as f:
                            first_line = f.readline().strip()
                            name = first_line.replace('# Pattern:', '').strip()

                        # Determine if this is a private or built-in pattern
                        is_private = patterns_dir == self.private_patterns_dir

                        patterns.append({
                            'pattern_id': pattern_id,
                            'name': name,
                            'file_path': file_path,
                            'is_private': is_private,
                            'source': 'private' if is_private else 'built-in'
                        })

                        seen_pattern_ids.add(pattern_id)

                    except Exception as e:
                        logger.warning("Error reading pattern file %s: %s", file_path, str(e))

        return sorted(patterns, key=lambda x: x['name'])

    def _parse_pattern_inputs(self, content: str) -> Tuple[List[PatternInput], List[InputGroup]]:
        """Parse pattern inputs and input groups from markdown content.

        Args:
            content: The markdown content to parse

        Returns:
            tuple[List[PatternInput], List[InputGroup]]: List of parsed pattern inputs and input groups
        """
        # Find the Pattern Inputs section
        if "## Pattern Inputs" not in content:
            return [], []

        try:
            # Extract the yaml block
            yaml_text = content.split("## Pattern Inputs")[1]
            yaml_block = yaml_text.split("```yaml")[1].split("```")[0]

            # Parse the yaml
            inputs_data = yaml.safe_load(yaml_block)

            # Convert to PatternInput objects
            pattern_inputs = [PatternInput.from_dict(input_data) for input_data in inputs_data.get('inputs', [])]

            # Parse input groups if present
            input_groups = []
            if 'input_groups' in inputs_data:
                input_groups = [InputGroup.from_dict(group_data) for group_data in inputs_data.get('input_groups', [])]

                # Validate groups - check that all input names in groups exist
                all_input_names = {input_obj.name for input_obj in pattern_inputs}

                # If group is specified in an input, but not defined in input_groups, create the group
                input_group_names = {group.name for group in input_groups}
                unique_groups_in_inputs = {
                    input_obj.group for input_obj in pattern_inputs
                    if input_obj.group and input_obj.group not in input_group_names
                }

                # Create implicit groups
                for group_name in unique_groups_in_inputs:
                    group_inputs = [input_obj.name for input_obj in pattern_inputs if input_obj.group == group_name]
                    new_group = InputGroup(
                        name=group_name,
                        description=f"Input group {group_name}",
                        required_inputs=1,
                        input_names=group_inputs
                    )
                    input_groups.append(new_group)

                # Validate all referenced inputs exist
                for group in input_groups:
                    for input_name in group.input_names:
                        if input_name not in all_input_names:
                            print_error_or_warnings(
                                f"Input group '{group.name}' references non-existent input '{input_name}'",
                                warning_only=True
                            )

                    # If no input_names specified, find all inputs with this group name
                    if not group.input_names:
                        group.input_names = [
                            input_obj.name for input_obj in pattern_inputs
                            if input_obj.group == group.name
                        ]

            return pattern_inputs, input_groups
        except Exception as e:
            print_error_or_warnings(f"Error parsing pattern inputs: {str(e)}")
            return [], []

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

            # Check for the 'results' key first, fall back to 'outputs' for backward compatibility
            outputs_list = outputs_data.get('results', outputs_data.get('outputs', []))
            pattern_outputs = [PatternOutput.from_dict(output_data) for output_data in outputs_list]

            return pattern_outputs
        except Exception as e:
            print_error_or_warnings(f"Error parsing pattern outputs: {str(e)}")
            return []

    def _parse_pattern_execution(self, content: str) -> Dict[str, Any]:
        """Parse pattern execution configuration from markdown content.

        Args:
            content: The markdown content to parse

        Returns:
            Dict[str, Any]: Dictionary with execution configuration
        """
        execution_config = {
            'handler': 'default',
            'prompt_for_confirmation': True,
            'show_visual_output_first': False
        }

        if "execution:" not in content:
            return execution_config

        try:
            # Find the execution configuration section within the Model Configuration
            config_section = content.split("## Model Configuration")[1]

            # Look for execution block
            if "execution:" in config_section:
                execution_text = config_section.split("execution:")[1]

                # Extract lines until the next section or end of YAML block
                execution_lines = []
                for line in execution_text.split('\n'):
                    stripped = line.strip()
                    if stripped.startswith('#') or stripped.startswith('format_instructions:') or stripped == "```":
                        break
                    execution_lines.append(line)

                # Join the execution lines and parse as YAML
                if execution_lines:
                    execution_yaml = '\n'.join(execution_lines)
                    parsed_execution = yaml.safe_load(execution_yaml)

                    if isinstance(parsed_execution, dict):
                        execution_config.update(parsed_execution)

            return execution_config
        except Exception as e:
            logger.warning("Error parsing execution configuration: %s", str(e))
            return execution_config

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
                if stripped == '```':
                    if in_yaml_block:  # Only break if we were in a YAML block
                        break
                if in_yaml_block:
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
            functionality = self._parse_pattern_functionality(content)
            model_config = self._parse_model_configuration(content)

            # Format instructions are now generated dynamically from output definitions
            # No need to extract from the pattern file
            format_instructions = None

            # The format_instructions will be generated when needed using the output definitions

            # Create complete configuration
            if purpose and functionality:
                return PatternConfiguration.from_components(
                    purpose=purpose,
                    functionality=functionality,
                    model_config=model_config,
                    format_instructions=format_instructions
                )
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
        # Search in priority order (private first, then built-in)
        for patterns_dir in self._get_pattern_directories():
            file_path = os.path.join(patterns_dir, f"{pattern_id}.md")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    inputs, input_groups = self._parse_pattern_inputs(content)
                    outputs = self._parse_pattern_outputs(content)
                    execution_config = self._parse_pattern_execution(content)

                    # Determine if this is a private pattern
                    is_private = patterns_dir == self.private_patterns_dir

                    return {
                        'prompt_content': self._parse_pattern_prompt(content),
                        'inputs': inputs,
                        'input_groups': input_groups,
                        'outputs': outputs,
                        'configuration': self._parse_pattern_configuration(content),
                        'execution': execution_config,
                        'pattern_id': pattern_id,
                        'file_path': file_path,
                        'is_private': is_private,
                        'source': 'private' if is_private else 'built-in'
                    }
                except Exception as e:
                    logger.error("Error reading pattern file %s: %s", file_path, str(e))
                    continue

        return None

    def _read_input_file(self, file_path: str) -> Optional[str]:
        """Read content from an input file.

        Args:
            file_path: Path to the input file

        Returns:
            Optional[str]: File content or None if file cannot be read
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
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
        input_groups = pattern_data['input_groups']

        if not inputs:
            return {}  # No inputs required

        # Create input dictionary for quick lookups
        input_dict = {input_def.name: input_def for input_def in inputs}
        result = {}

        # Map inputs to their groups
        group_to_inputs = {}
        for group in input_groups:
            group_to_inputs[group.name] = [input_name for input_name in group.input_names
                                          if input_name in input_dict]  # Filter valid inputs

        # Create reverse mapping of input to group
        input_to_group = {}
        for group_name, input_names in group_to_inputs.items():
            for input_name in input_names:
                input_to_group[input_name] = group_name

        # Track which inputs from a group have been provided/processed
        processed_group_inputs = {group.name: set() for group in input_groups}

        # Start with provided JSON values
        if input_values:
            result.update(input_values)

            # Mark inputs from groups as processed
            for input_name in input_values.keys():
                if input_name in input_to_group:
                    group_name = input_to_group[input_name]
                    processed_group_inputs[group_name].add(input_name)

        # Process input groups first if in interactive mode
        if interactive:
            for group in input_groups:
                valid_inputs = [input_dict[name] for name in group.input_names if name in input_dict]

                if not valid_inputs:
                    continue  # Skip empty groups

                # Skip if we already have enough inputs from this group
                if len(processed_group_inputs[group.name]) >= group.required_inputs:
                    continue

                # Ask which input(s) from the group to provide
                print(f"\n{group.description}")
                print(f"Select which input(s) to provide ({group.required_inputs} required):")

                # Display available inputs in the group
                available_inputs = []
                for i, input_def in enumerate(valid_inputs, 1):
                    if input_def.name not in result:
                        print(f"{i}. {input_def.name}: {input_def.description}")
                        available_inputs.append(input_def)

                if not available_inputs:
                    continue  # All inputs in this group already provided

                # Get user selection(s)
                selections = []
                while len(selections) < group.required_inputs:
                    choice = input(f"Select input number (1-{len(available_inputs)}): ").strip()

                    try:
                        choice_num = int(choice)
                        if 1 <= choice_num <= len(available_inputs):
                            selected_input = available_inputs[choice_num - 1]
                            if selected_input in selections:
                                print(f"You've already selected {selected_input.name}")
                                continue

                            selections.append(selected_input)
                            processed_group_inputs[group.name].add(selected_input.name)

                            # If we've selected enough inputs, break
                            if len(selections) >= group.required_inputs:
                                break

                            # If more selections are needed, ask if user wants to add another
                            if len(selections) < group.required_inputs:
                                print(f"Selected {len(selections)} of {group.required_inputs} required inputs.")
                            elif group.required_inputs < len(available_inputs):
                                add_more = input("Add more inputs from this group? (y/n): ").lower()
                                if add_more != 'y':
                                    break
                        else:
                            print(f"Please enter a number between 1 and {len(available_inputs)}")
                    except ValueError:
                        print("Please enter a valid number")

                # Now get values for each selected input
                for selected_input in selections:
                    self._get_input_value(selected_input, result)

        # Handle remaining inputs that are not part of any group
        i = 0
        while i < len(inputs):
            input_def = inputs[i]

            # Skip if already in result or part of a processed group
            if input_def.name in result or (input_def.group and
                                            input_def.name in processed_group_inputs.get(input_def.group, set())):
                i += 1
                continue

            # Skip if part of a group (those were handled above)
            if input_def.group and interactive:
                i += 1
                continue

            # Handle non-interactive mode and ignored undefined inputs
            if not interactive or (not input_def.required and input_def.ignore_undefined):
                if input_def.required and not input_def.ignore_undefined:
                    # Check if this is part of a group and if the group requirements are met
                    if input_def.group and len(processed_group_inputs.get(input_def.group, set())) >= next(
                            (g.required_inputs for g in input_groups if g.name == input_def.group), 1):
                        i += 1
                        continue

                    print_error_or_warnings(f"Required input '{input_def.name}' is missing")
                    return None

                # Set default value for non-required inputs that can be ignored
                if not input_def.required and input_def.ignore_undefined:
                    result[input_def.name] = input_def.default
                i += 1
                continue

            # Interactive input for non-grouped inputs or in non-interactive mode
            self._get_input_value(input_def, result)
            i += 1

        # Validate group requirements
        for group in input_groups:
            provided_count = sum(1 for input_name in group.input_names if input_name in result)
            if provided_count < group.required_inputs:
                print_error_or_warnings(
                    f"Group '{group.name}' requires at least {group.required_inputs} input(s), "
                    f"but only {provided_count} provided"
                )
                return None

        return result

    def _get_input_value(self, input_def: PatternInput, result: Dict[str, Any]) -> None:
        """Get and validate a value for a specific input.

        Args:
            input_def: The input definition
            result: Dictionary to store the result in
        """
        while True:
            print(f"\n{input_def.description}")
            if input_def.input_type == InputType.SELECT:
                print("Options:", ", ".join(input_def.options or []))

            if not input_def.required:
                print("(Optional - press Enter to skip)")

            value = input(f"{input_def.name}: ").strip()

            if not value:
                if not input_def.required:
                    result[input_def.name] = input_def.default
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
            # For IMAGE_FILE type, preserve the path to use with -img parameter
            elif input_def.input_type == InputType.IMAGE_FILE:
                # Store the file path directly for image files
                result[input_def.name] = value
            # For PDF_FILE type, preserve the path to use with -pdf parameter
            elif input_def.input_type == InputType.PDF_FILE:
                # Store the file path directly for PDF files
                result[input_def.name] = value
            else:
                result[input_def.name] = value

            break

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
        print("-" * 70)

        # Display patterns with index
        for i, pattern in enumerate(patterns, 1):
            source_indicator = "🔒" if pattern.get('is_private', False) else "📦"
            print(f"{i}. {pattern['name']} {source_indicator}")
            print(f"   ID: {pattern['pattern_id']} ({pattern.get('source', 'built-in')})")
            print("-" * 70)

        print("\nOptions:")
        print(f"1-{len(patterns)}. Select pattern")
        print("q. Quit")
        print("\n🔒 = Private pattern, 📦 = Built-in pattern")

        while True:
            choice = input(f"\nEnter your choice (1-{len(patterns)} or q): ").lower()

            if choice == 'q':
                return None

            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(patterns):
                    return patterns[choice_num - 1]['pattern_id']
                print(f"Please enter a number between 1 and {len(patterns)}")
            except ValueError:
                print("Please enter a valid number or 'q' to quit")

    def process_pattern_response(
        self, pattern_id: str, response: Union[str, Dict], output_handler
    ) -> Tuple[str, List[str]]:
        """Process a response for a specific pattern.

        This method handles pattern-specific processing of AI responses,
        delegating the actual output handling to output_handler.

        Args:
            pattern_id: ID of the pattern
            response: Response from the AI service
            output_handler: Instance of OutputHandler

        Returns:
            Tuple[str, List[str]]: (formatted output, list of created files)
        """
        logger.debug("Processing pattern response for %s", pattern_id)

        pattern_data = self.get_pattern_content(pattern_id)
        if not pattern_data:
            logger.warning("Pattern %s not found", pattern_id)
            return "Pattern not found", []

        pattern_outputs = pattern_data.get('outputs', [])
        execution_config = pattern_data.get('execution', {})

        # Get output configuration
        output_config = {
            'pattern_id': pattern_id,
            'execution': execution_config
        }

        # Delegate to output handler for processing
        return output_handler.process_output(
            response=response,
            output_config=output_config,
            console_output=True,
            file_output=True,
            pattern_outputs=pattern_outputs
        )
