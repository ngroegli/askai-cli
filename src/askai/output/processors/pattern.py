"""Pattern output processing.

This module handles processing pattern-based outputs from AI responses,
including categorizing outputs, extracting pattern contents, and managing
pattern-specific file operations.
"""

import re
import logging
from typing import List, Tuple, Dict, Union, Optional
from pathlib import Path

from askai.core.patterns.outputs import PatternOutput, OutputAction

logger = logging.getLogger(__name__)

class PatternProcessor:
    """Processes pattern-based outputs from AI responses."""

    def __init__(self, content_extractor, directory_manager, file_writer_chain):
        """Initialize the pattern processor.

        Args:
            content_extractor: ContentExtractor instance
            directory_manager: DirectoryManager instance
            file_writer_chain: FileWriterChain instance
        """
        self.content_extractor = content_extractor
        self.directory_manager = directory_manager
        self.file_writer_chain = file_writer_chain

    def handle_pattern_outputs(self, response: Union[str, Dict], pattern_outputs: List[PatternOutput]) -> List[str]:
        """Handle pattern-based outputs.

        Args:
            response: AI response containing the outputs
            pattern_outputs: List of pattern output definitions

        Returns:
            List of created file paths
        """
        created_files = []

        if not pattern_outputs:
            return created_files

        try:
            # Get output directory if needed for file outputs
            output_dir = self._get_output_dir_if_needed(pattern_outputs)
            if output_dir is None and any(output.action == OutputAction.WRITE for output in pattern_outputs):
                logger.warning("No output directory available for file outputs")
                return created_files

            # Extract pattern contents from response
            pattern_contents = self.extract_pattern_contents(response, pattern_outputs)

            # Process outputs in definition order
            for output in pattern_outputs:
                if output.name in pattern_contents:
                    content = pattern_contents[output.name]

                    if output.action == OutputAction.WRITE:
                        # Process file output
                        self._process_file_output(output, content, output_dir, created_files)

                    elif output.action == OutputAction.DISPLAY:
                        # Display output will be handled by output coordinator
                        logger.info("Display output '%s': %s", output.name, content[:100])

                    elif output.action == OutputAction.EXECUTE:
                        # Command execution will be handled by output coordinator after display
                        logger.info("Command output '%s': %s", output.name, content)

        except Exception as e:
            logger.error("Error handling pattern outputs: %s", str(e))

        return created_files

    def _categorize_outputs(self, pattern_outputs: List[PatternOutput]) -> Tuple[
        List[PatternOutput], List[PatternOutput], List[PatternOutput]
    ]:
        """Categorize pattern outputs by type.

        Args:
            pattern_outputs: List of pattern outputs to categorize

        Returns:
            Tuple of (file_outputs, display_outputs, command_outputs)
        """
        file_outputs = []
        display_outputs = []
        command_outputs = []

        for output in pattern_outputs:
            if output.action == OutputAction.WRITE:
                file_outputs.append(output)
            elif output.action == OutputAction.DISPLAY:
                display_outputs.append(output)
            elif output.action == OutputAction.EXECUTE:
                command_outputs.append(output)

        return file_outputs, display_outputs, command_outputs

    def _get_output_dir_if_needed(self, pattern_outputs: List[PatternOutput]) -> Optional[str]:
        """Get output directory if file outputs exist."""
        file_outputs_exist = any(output.action == OutputAction.WRITE for output in pattern_outputs)
        if file_outputs_exist:
            return self.directory_manager.get_output_directory()
        return None

    def _process_file_output(self, output: PatternOutput, content: str,
                            output_dir: Optional[str], created_files: List[str]) -> None:
        """Process a single file output."""
        if content and output_dir:
            file_path = self._get_output_file_path(output, output_dir)
            if file_path:
                success = self.file_writer_chain.write_by_extension(content, file_path)
                if success:
                    created_files.append(file_path)
                    logger.info("Created file: %s", file_path)

    def extract_pattern_contents(
            self, response: Union[str, Dict], pattern_outputs: List[PatternOutput]
            ) -> Dict[str, str]:
        """Extract content for each pattern output.

        Args:
            response: AI response to extract from
            pattern_outputs: Pattern outputs to extract content for

        Returns:
            Dict mapping output names to extracted content
        """
        contents = {}

        # Get the response text
        if isinstance(response, dict):
            if 'content' in response:
                text = response['content']
            else:
                text = str(response)
        else:
            text = str(response)

        # Try to extract structured data first
        structured_data = self.content_extractor.extract_structured_data(response)
        logger.debug("Extracted structured data: %s", structured_data)

        # Extract content for each pattern output
        for output in pattern_outputs:
            content = None

            # First try to get from structured data
            if output.name in structured_data:
                content = structured_data[output.name]

            # If not found, try pattern-based extraction
            if not content:
                content = self._extract_output_content_from_response(text, output)

            if content:
                contents[output.name] = str(content).strip()
            else:
                logger.warning("No content found for output: %s", output.name)

        return contents

    def _extract_output_content_from_response(self, text: str, output: PatternOutput) -> Optional[str]:
        """Extract content for a specific output from response text.

        Args:
            text: Response text to extract from
            output: Pattern output definition

        Returns:
            Extracted content or None
        """
        output_name = output.name.lower()

        # Define search patterns for common output names
        patterns = []

        # Add specific patterns based on output name
        if 'html' in output_name or 'page' in output_name:
            patterns.extend([
                rf'{re.escape(output.name)}:\s*```html\s*\n(.*?)\n```',
                rf'{re.escape(output.name)}:\s*```\s*\n(<!DOCTYPE.*?</html>)\s*\n```',
                r'```html\s*\n(.*?)\n```',
                r'(<!DOCTYPE html.*?</html>)',
            ])
        elif 'css' in output_name or 'style' in output_name:
            patterns.extend([
                rf'{re.escape(output.name)}:\s*```css\s*\n(.*?)\n```',
                r'```css\s*\n(.*?)\n```',
            ])
        elif 'js' in output_name or 'javascript' in output_name:
            patterns.extend([
                rf'{re.escape(output.name)}:\s*```javascript\s*\n(.*?)\n```',
                rf'{re.escape(output.name)}:\s*```js\s*\n(.*?)\n```',
                r'```javascript\s*\n(.*?)\n```',
                r'```js\s*\n(.*?)\n```',
            ])
        elif 'json' in output_name:
            patterns.extend([
                rf'{re.escape(output.name)}:\s*```json\s*\n(.*?)\n```',
                r'```json\s*\n(.*?)\n```',
            ])
        else:
            # Generic patterns
            patterns.extend([
                rf'{re.escape(output.name)}:\s*```\w*\s*\n(.*?)\n```',
                rf'{re.escape(output.name)}:\s*(.+?)(?=\n\w+:|$)',
                rf'## {re.escape(output.name)}\s*\n(.*?)(?=\n##|$)',
                rf'\*\*{re.escape(output.name)}\*\*:\s*(.+?)(?=\n|$)',
            ])

        # Try each pattern
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE | re.IGNORECASE)
            if matches:
                content = matches[0].strip()
                return self.content_extractor.clean_escaped_content(content)

        return None

    def _get_output_file_path(self, output: PatternOutput, output_dir: str) -> Optional[str]:
        """Get the file path for a pattern output.

        Args:
            output: Pattern output definition
            output_dir: Base output directory

        Returns:
            Full file path or None if invalid
        """
        if not output_dir or not output.write_to_file:
            return None

        try:
            # PatternOutput uses write_to_file for filename
            file_path = Path(output_dir) / output.write_to_file
            return str(file_path.resolve())

        except Exception as e:
            logger.error("Error creating file path for output %s: %s", output.name, str(e))
            return None
