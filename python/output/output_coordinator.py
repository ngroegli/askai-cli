"""Output coordination and orchestration.

This module provides the main OutputCoordinator class that orchestrates
all output processing operations through specialized processors.
"""

import logging
import json
import os
from typing import Optional, Dict, List, Tuple, Any, Union

from python.patterns.pattern_outputs import PatternOutput, OutputAction
from python.output.display_formatters.terminal_formatter import TerminalFormatter
from python.output.display_formatters.markdown_formatter import MarkdownFormatter
from python.output.file_writers.file_writer_chain import FileWriterChain
from python.output.processors.content_extractor import ContentExtractor
from python.output.processors.pattern_processor import PatternProcessor
from python.output.processors.response_normalizer import ResponseNormalizer
from python.output.processors.directory_manager import DirectoryManager

logger = logging.getLogger(__name__)

class OutputCoordinator:
    """Coordinates all output processing operations.

    This class serves as the main facade for output handling, orchestrating
    the work of specialized processors while maintaining a clean interface
    for the rest of the application.
    """

    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the output coordinator.

        Args:
            output_dir: Directory for saving output files
        """
        self.output_dir = output_dir

        # Initialize components
        self.response_normalizer = ResponseNormalizer()
        self.content_extractor = ContentExtractor()
        self.directory_manager = DirectoryManager(output_dir)
        self.file_writer_chain = FileWriterChain()

        # Initialize pattern processor with dependencies
        self.pattern_processor = PatternProcessor(
            self.content_extractor,
            self.directory_manager,
            self.file_writer_chain
        )

        # Initialize formatters
        self.formatters = {
            'console': TerminalFormatter(),
            'markdown': MarkdownFormatter()
        }

        # Storage for pending commands to execute after display
        self.pending_commands = []
        # Storage for pending file operations to execute after display
        self.pending_files = []

    def process_output(
            self,
            response: Union[str, Dict],
            output_config: Optional[Dict[str, Any]] = None,
            console_output: bool = True,
            file_output: bool = False,
            pattern_outputs: Optional[List[PatternOutput]] = None
    ) -> Tuple[str, List[str]]:
        """Process AI output based on configuration.

        This method is the main entry point for handling output from the AI service.
        It determines what type of output is present and routes it to the appropriate
        handling method.

        Args:
            response: The raw output from the AI (can be string or dict)
            output_config: Configuration for output processing
            console_output: Whether to format for console output
            file_output: Whether to save output to files
            pattern_outputs: Pattern-defined outputs from pattern definition

        Returns:
            Tuple of (formatted_output_string, list_of_created_files)
        """
        try:
            # Normalize the response to a consistent format
            normalized_response = self.response_normalizer.normalize_response(response)

            created_files = []

            # Handle pattern-based outputs if provided
            if pattern_outputs:
                if console_output:
                    # Extract pattern contents once for both display and file operations
                    pattern_contents = self.pattern_processor.extract_pattern_contents(response, pattern_outputs)

                    # Process outputs in definition order for display and command storage
                    formatted_output = self._process_pattern_outputs_in_order(pattern_contents, pattern_outputs)

                    # Store file creation info for later (after display is shown)
                    self._store_file_creation_info(pattern_contents, pattern_outputs)
                    created_files = []  # Will be populated when files are actually created
                else:
                    # For non-console output, just handle file creation
                    created_files = self.pattern_processor.handle_pattern_outputs(response, pattern_outputs)
                    formatted_output = normalized_response
            else:
                # Handle standard output (non-pattern)
                formatted_output, standard_files = self._handle_standard_output(
                    response, output_config, console_output, file_output
                )
                created_files.extend(standard_files)

            return formatted_output, created_files

        except Exception as e:
            logger.error("Error processing output: %s", str(e))
            fallback_response = self.response_normalizer.normalize_response(response)
            return fallback_response, []

    def _handle_standard_output(
            self,
            response: Union[str, Dict],
            output_config: Optional[Dict[str, Any]],
            console_output: bool,
            file_output: bool
    ) -> Tuple[str, List[str]]:
        """Handle standard (non-pattern) output processing.

        Args:
            response: AI response
            output_config: Output configuration
            console_output: Whether to format for console
            file_output: Whether to save to files

        Returns:
            Tuple of (formatted_output, created_files)
        """
        created_files = []

        # Normalize response
        normalized_response = self.response_normalizer.normalize_response(response)

        # Extract content if file output is requested
        if file_output and self.output_dir:
            file_created = self._extract_and_save_content(
                response, output_config or {}
            )
            if file_created:
                created_files.append(file_created)

        # Format for console output
        if console_output:
            format_type = output_config.get('format', 'rawtext') if output_config else 'rawtext'
            if format_type == 'md':
                formatted_output = self.formatters['markdown'].format(normalized_response)
            else:
                formatted_output = self.formatters['console'].format(normalized_response)
        else:
            formatted_output = normalized_response

        return formatted_output, created_files

    def _extract_and_save_content(
            self,
            response: Union[str, Dict],
            output_config: Dict[str, Any]
    ) -> Optional[str]:
        """Extract and save content from response.

        Args:
            response: AI response to extract from
            output_config: Configuration for output

        Returns:
            Path of created file or None
        """
        try:
            # Extract structured data
            structured_data = self.content_extractor.extract_structured_data(response)

            # Handle different output formats based on config
            if 'json_filename' in output_config and structured_data:
                json_content = json.dumps(structured_data, indent=2)
                return self._write_to_file(json_content, output_config['json_filename'])

            if 'markdown_filename' in output_config:
                # Save as markdown
                normalized_response = self.response_normalizer.normalize_response(response)
                return self._write_to_file(normalized_response, output_config['markdown_filename'])

            # Handle HTML/CSS/JS if present in structured data
            files_created = []
            if 'html' in structured_data:
                html_file = self._write_to_file(structured_data['html'], 'index.html')
                if html_file:
                    files_created.append(html_file)

            if 'css' in structured_data:
                css_file = self._write_to_file(structured_data['css'], 'styles.css')
                if css_file:
                    files_created.append(css_file)

            if 'javascript' in structured_data:
                js_file = self._write_to_file(structured_data['javascript'], 'script.js')
                if js_file:
                    files_created.append(js_file)

            # Return the first created file (for compatibility)
            return files_created[0] if files_created else None

        except Exception as e:
            logger.error("Error extracting and saving content: %s", str(e))
            return None

    def _write_to_file(
            self,
            content: str,
            filename: str,
            subdirectory: Optional[str] = None
    ) -> Optional[str]:
        """Write content to a file in the output directory.

        Args:
            content: Content to write
            filename: Name of the file
            subdirectory: Optional subdirectory within output dir

        Returns:
            Optional[str]: File path if successful, None otherwise
        """
        if not self.output_dir:
            return None

        try:
            # Handle subdirectory if provided
            if subdirectory:
                dir_path = os.path.join(self.output_dir, subdirectory)
                os.makedirs(dir_path, exist_ok=True)
                file_path = os.path.join(dir_path, filename)
            else:
                file_path = os.path.join(self.output_dir, filename)

            # Use the unified write_by_extension method that handles all file types
            # The file_writer will extract the extension from the file path
            success = self.file_writer_chain.write_by_extension(content, file_path)

            return file_path if success else None
        except Exception as e:
            logger.error("Error writing to file %s: %s", filename, str(e))
            return None

    def _format_pattern_response(self, response: str) -> str:
        """Format response for pattern-based outputs.

        Args:
            response: Normalized response

        Returns:
            Formatted response string
        """
        # For now, just return the console-formatted response
        # This could be enhanced to show pattern-specific formatting
        return self.formatters['console'].format(response)

    def _format_pattern_contents(self, pattern_contents: Dict[str, str], pattern_outputs: List) -> str:
        """Format extracted pattern contents for display.

        Args:
            pattern_contents: Dict mapping output names to extracted content
            pattern_outputs: List of pattern output definitions

        Returns:
            Formatted string for display
        """
        if not pattern_contents:
            return "No pattern content found"

        formatted_parts = []
        for output in pattern_outputs:
            if output.name in pattern_contents:
                content = pattern_contents[output.name]
                formatted_parts.append(f"{output.name.upper()}:\n{content}\n")

        if formatted_parts:
            return "\n".join(formatted_parts)
        return "No content found for any pattern outputs"

    def _process_pattern_outputs_in_order(self, pattern_contents: Dict[str, str], pattern_outputs: List) -> str:
        """Process pattern outputs in their definition order, handling displays and storing commands.

        Args:
            pattern_contents: Dict mapping output names to extracted content
            pattern_outputs: List of pattern output definitions in their definition order

        Returns:
            Formatted string for display outputs only
        """
        if not pattern_contents:
            return "No pattern content found"

        # Clear any existing pending commands
        self.pending_commands = []

        formatted_parts = []

        # Process outputs in definition order
        for i, output in enumerate(pattern_outputs):
            if output.name in pattern_contents:
                content = pattern_contents[output.name]

                if output.action == OutputAction.DISPLAY:
                    # Add to formatted output immediately
                    formatted_parts.append(f"{output.name.upper()}:\n{content}\n")

                elif output.action == OutputAction.EXECUTE:
                    # Check if there are any display outputs after this command
                    has_display_after = any(
                        later_output.action == OutputAction.DISPLAY
                        for later_output in pattern_outputs[i+1:]
                        if later_output.name in pattern_contents
                    )

                    if has_display_after:
                        # Execute immediately since there are displays coming after
                        PatternOutput.execute_command(content, output.name)
                    else:
                        # Store for later execution (traditional behavior when command is last)
                        self.pending_commands.append((i, content, output.name))

        if formatted_parts:
            return "\n".join(formatted_parts)
        return "No display content found for any pattern outputs"

    def _execute_pattern_commands(self, pattern_contents: Dict[str, str], pattern_outputs: List) -> None:
        """Execute commands from pattern outputs after display content has been shown.

        Args:
            pattern_contents: Dict mapping output names to extracted content
            pattern_outputs: List of pattern output definitions
        """
        for output in pattern_outputs:
            if output.action == OutputAction.EXECUTE and output.name in pattern_contents:
                command = pattern_contents[output.name]
                PatternOutput.execute_command(command, output.name)

    def execute_pending_operations(self) -> List[str]:
        """Execute any pending operations (commands and file creation) after display.

        Returns:
            List of created file paths
        """
        created_files = []

        # Execute pending commands first (if any)
        sorted_commands = sorted(self.pending_commands, key=lambda x: x[0])
        for _, command, output_name in sorted_commands:
            PatternOutput.execute_command(command, output_name)

        # Then handle file creation
        if self.pending_files:
            # Get output directory for file creation
            output_dir = self.directory_manager.get_output_directory()
            if output_dir:
                for content, output in self.pending_files:
                    file_path = self._get_output_file_path(output, output_dir)
                    if file_path:
                        success = self.file_writer_chain.write_by_extension(content, file_path)
                        if success:
                            created_files.append(file_path)
                            logger.info("Created file: %s", file_path)

        # Clear pending operations after execution
        self.pending_commands = []
        self.pending_files = []

        return created_files

    def _store_file_creation_info(self, pattern_contents: Dict[str, str], pattern_outputs: List[PatternOutput]) -> None:
        """Store file creation information for later execution after display.

        Args:
            pattern_contents: Dict mapping output names to extracted content
            pattern_outputs: List of pattern output definitions
        """
        # Clear any existing pending files
        self.pending_files = []

        for output in pattern_outputs:
            if output.action == OutputAction.WRITE and output.name in pattern_contents:
                content = pattern_contents[output.name]
                if content:
                    self.pending_files.append((content, output))

    def _create_pattern_files(
        self, pattern_contents: Dict[str, str], pattern_outputs: List[PatternOutput]
    ) -> List[str]:
        """Create files from pattern outputs using already extracted content.

        Args:
            pattern_contents: Dict mapping output names to extracted content
            pattern_outputs: List of pattern output definitions

        Returns:
            List of created file paths
        """
        created_files = []

        # Get output directory if needed for file outputs
        output_dir = None
        file_outputs_exist = any(output.action == OutputAction.WRITE for output in pattern_outputs)
        if file_outputs_exist:
            output_dir = self.directory_manager.get_output_directory()
            if output_dir is None:
                logger.warning("No output directory available for file outputs")
                return created_files

        # Process file outputs only
        for output in pattern_outputs:
            if output.action == OutputAction.WRITE and output.name in pattern_contents:
                content = pattern_contents[output.name]
                if content and output_dir:
                    file_path = self._get_output_file_path(output, output_dir)
                    if file_path:
                        success = self.file_writer_chain.write_by_extension(content, file_path)
                        if success:
                            created_files.append(file_path)
                            logger.info("Created file: %s", file_path)

        return created_files

    def _get_output_file_path(self, output: PatternOutput, output_dir: str) -> Optional[str]:
        """Get the file path for a pattern output.

        Args:
            output: Pattern output definition
            output_dir: Output directory path

        Returns:
            Full file path or None if not applicable
        """
        if hasattr(output, 'write_to_file') and output.write_to_file:
            return os.path.join(output_dir, output.write_to_file)
        return None
