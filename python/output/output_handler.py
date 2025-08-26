"""
Output handling module for askai-cli.

This module handles all output processing from AI responses, including:
- Extracting different content types (HTML, CSS, JS, markdown, etc.)
- Formatting content for console display
- Writing content to files
- Processing pattern-based outputs with structured content
- Executing commands based on output actions
"""

import os
import json
import re
import logging
import traceback
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any, Union

from patterns.pattern_outputs import PatternOutput, OutputType, OutputAction
from python.output.formatters.console_formatter import ConsoleFormatter
from python.output.formatters.markdown_formatter import MarkdownFormatter
from python.output.file_writer import FileWriter

logger = logging.getLogger(__name__)

class OutputHandler:
    """Handler for processing AI outputs and handling all output actions.

    This class processes output from the AI service, extracts content in various formats,
    formats it for display, and handles writing to files or executing commands.
    """

    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the OutputHandler with optional output directory.

        Args:
            output_dir: Directory for saving output files
        """
        self.output_dir = output_dir

        # Initialize formatters
        self.formatters = {
            'console': ConsoleFormatter(),
            'markdown': MarkdownFormatter()
        }

        # Initialize file writer
        self.file_writer = FileWriter(output_dir=output_dir, logger=logger)

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
            Tuple[str, List[str]]: The formatted output and list of created files
        """
        # Initialize output configuration
        output_config = output_config or {}

        # For pattern-specific response handling
        pattern_id = output_config.get('pattern_id')
        if pattern_id:
            logger.debug("Using pattern-specific output handling for %s", pattern_id)

        # Get normalized string representation of response (preserving original)
        response_text = self._normalize_response(response)

        # Handle pattern outputs in standardized way
        if pattern_outputs:
            logger.info("Processing pattern outputs: %d outputs defined", len(pattern_outputs))
            # Log each output for debugging
            for i, output in enumerate(pattern_outputs):
                logger.info("  Output %d: name=%s, type=%s, action=%s",
                            i+1, output.name, output.output_type, output.action)
            return self._handle_standardized_pattern_output(response, pattern_outputs, output_config)

        # For regular output without pattern definitions
        return self._handle_standard_output(response, response_text, output_config, console_output, file_output)

    def _normalize_response(self, response: Union[str, Dict]) -> str:
        """Convert response to a normalized string representation.

        Args:
            response: The raw AI response

        Returns:
            str: Normalized string representation
        """
        # String response needs no conversion
        if isinstance(response, str):
            return response

        # Handle dictionary response
        if isinstance(response, dict):
            # Common response formats from various APIs
            if 'content' in response:
                return response['content']
            if 'text' in response:
                return response['text']
            if 'message' in response:
                return response['message']
            # API formats with nested choices
            if ('choices' in response and
                  isinstance(response['choices'], list) and
                  response['choices']):
                for choice in response['choices']:
                    if isinstance(choice, dict):
                        if 'message' in choice and 'content' in choice['message']:
                            return choice['message']['content']
                        if 'text' in choice:
                            return choice['text']

            # Fallback to JSON serialization
            try:
                return json.dumps(response, indent=2)
            except Exception:
                return str(response)

        # Fallback for other types
        return str(response)

    def _handle_standard_output(self,
                              response: Union[str, Dict],
                              response_text: str,
                              output_config: Optional[Dict[str, Any]],
                              console_output: bool,
                              file_output: bool) -> Tuple[str, List[str]]:
        """Handle standard output without pattern definitions.

        Args:
            response: The original AI response
            response_text: Normalized text representation
            output_config: Output configuration
            console_output: Whether to format for console
            file_output: Whether to save to files

        Returns:
            Tuple[str, List[str]]: Formatted output and created files
        """
        output_config = output_config or {}
        created_files = []

        # Extract and save content to files if requested
        if file_output and self.output_dir:
            created_files = self._extract_and_save_content(response, response_text, output_config)

        # Format output for console if requested
        formatted_output = response_text
        if console_output:
            output_format = output_config.get('format', 'rawtext')
            if output_format == 'md':
                # Check if we should render the markdown or output it as plain text
                plain_md = output_config.get('plain_md', False)
                if plain_md:
                    # Just use the raw text for plain markdown output
                    formatted_output = response_text
                else:
                    # Render the markdown for display in the console
                    formatted_output = self.formatters['console'].format(response_text, content_type='markdown')
            else:
                formatted_output = self.formatters['console'].format(response_text)

        return formatted_output, created_files

    def _extract_and_save_content(self,
                               response: Union[str, Dict],
                               response_text: str,
                               output_config: Dict[str, Any]) -> List[str]:
        """Save content from the response to files based on output_config.

        Args:
            response: The original AI response
            response_text: Normalized text representation
            output_config: Output configuration

        Returns:
            List[str]: List of created file paths
        """
        created_files = []
        content_to_save = response_text

        # Check if we have structured data with results
        structured_data = {}
        if isinstance(response, dict):
            if 'results' in response:
                structured_data = response['results']
            elif 'content' in response and isinstance(response['content'], str):
                # Try to parse the content as JSON
                try:
                    content_json = json.loads(response['content'])
                    if isinstance(content_json, dict) and 'results' in content_json:
                        structured_data = content_json['results']
                except (json.JSONDecodeError, TypeError):
                    # Not valid JSON, use as is
                    content_to_save = response['content']

        # If we have structured data, extract specific content types
        if structured_data:
            # HTML content
            if 'html' in structured_data and isinstance(structured_data['html'], str):
                html_filename = output_config.get('html_filename', 'output.html')
                file_path = self._write_to_file(structured_data['html'], html_filename)
                if file_path:
                    created_files.append(file_path)
                    logger.info("HTML content saved to %s", file_path)

            # CSS content
            if 'css' in structured_data and isinstance(structured_data['css'], str):
                css_filename = output_config.get('css_filename', 'styles.css')
                file_path = self._write_to_file(structured_data['css'], css_filename)
                if file_path:
                    created_files.append(file_path)
                    logger.info("CSS content saved to %s", file_path)

            # JavaScript content
            if 'javascript' in structured_data and isinstance(structured_data['javascript'], str):
                js_filename = output_config.get('js_filename', 'script.js')
                file_path = self._write_to_file(structured_data['javascript'], js_filename)
                if file_path:
                    created_files.append(file_path)
                    logger.info("JavaScript content saved to %s", file_path)

            # JSON content
            if 'json' in structured_data:
                json_content = structured_data['json']
                json_filename = output_config.get('json_filename', 'data.json')
                # Format JSON content appropriately
                if isinstance(json_content, (dict, list)):
                    json_str = json.dumps(json_content, indent=2)
                else:
                    json_str = str(json_content)
                file_path = self._write_to_file(json_str, json_filename)
                if file_path:
                    created_files.append(file_path)
                    logger.info("JSON content saved to %s", file_path)

            # Markdown content
            if 'markdown' in structured_data and isinstance(structured_data['markdown'], str):
                markdown_filename = output_config.get('markdown_filename', 'output.md')
                file_path = self._write_to_file(structured_data['markdown'], markdown_filename)
                if file_path:
                    created_files.append(file_path)
                    logger.info("Markdown content saved to %s", file_path)

        # If no specific content was found but we have a filename, save the raw content
        if not created_files:
            # Try to save as markdown if markdown_filename is specified
            if output_config.get('markdown_filename'):
                markdown_filename = output_config.get('markdown_filename')
                if markdown_filename:  # Ensure filename is not None
                    file_path = self._write_to_file(content_to_save, markdown_filename)
                    if file_path:
                        created_files.append(file_path)
                        logger.info("Content saved as markdown to %s", file_path)
            # Try to save as JSON if json_filename is specified
            elif output_config.get('json_filename'):
                json_filename = output_config.get('json_filename')
                # Ensure filename is not None
                if json_filename:
                    # Try to parse as JSON first
                    try:
                        json_obj = json.loads(content_to_save) if isinstance(content_to_save, str) else content_to_save
                        json_str = json.dumps(json_obj, indent=2)
                        file_path = self._write_to_file(json_str, json_filename)
                    except (json.JSONDecodeError, TypeError):
                        # If not valid JSON, save as is
                        file_path = self._write_to_file(str(content_to_save), json_filename)

                    if file_path:
                        created_files.append(file_path)
                        logger.info("Content saved as JSON to %s", file_path)

        return created_files

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
            success = self.file_writer.write_by_extension(content, file_path)

            return file_path if success else None
        except Exception as e:
            logger.error("Error writing to file %s: %s", filename, str(e))
            return None

    def _handle_standardized_pattern_output(
            self,
            response: Union[str, Dict],
            pattern_outputs: List[PatternOutput],
            _output_config: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, List[str]]:
        # Note: output_config parameter is not used but kept for API consistency
        # Adding underscore prefix to indicate it's intentionally unused
        """Handle standardized pattern outputs.

        This method processes outputs based on pattern definitions.
        Each output is handled according to its type and action.

        Args:
            response: The AI response
            pattern_outputs: List of pattern outputs
            output_config: Optional output configuration

        Returns:
            Tuple[str, List[str]]: The formatted output and list of created files
        """

        # Extract structured data from response
        structured_data = self._extract_structured_data(response)
        logger.debug("Extracted structured data keys: %s", list(structured_data.keys()))

        # Log more detailed information about structured data for debugging
        logger.info("STRUCTURED DATA DUMP: %s", structured_data)

        # Log more detailed information about the response for debugging
        if isinstance(response, dict):
            logger.debug("Response type: dictionary with keys %s", list(response.keys()))
            if 'content' in response:
                logger.debug("Response content sample: %s", response['content'][:200] + "...")
        else:
            logger.debug("Response type: %s", type(response))

        # Prepare outputs
        created_files = []
        visual_content = None

        # Check if we have usable data
        if not structured_data:
            # Construct error message for invalid pattern output
            error_msg = (
                "Pattern output requires a valid JSON structure "
                "with 'results' field containing outputs"
            )
            logger.error(error_msg)
            # Try to return raw content instead of error
            if isinstance(response, dict) and 'content' in response:
                return response['content'], []
            return error_msg, []

        # Get output directory with user confirmation for file operations
        output_dir = None
        if any(output.action == OutputAction.WRITE for output in pattern_outputs):
            output_dir = self._get_output_directory()

        # Extract and assign content from response to outputs
        self._extract_output_content_from_response(pattern_outputs, structured_data, response)

        # Track outputs in the original order from pattern definition
        ordered_outputs = []
        for output in pattern_outputs:
            # Skip outputs with no content
            if not output.get_content():
                continue
            ordered_outputs.append(output)

        logger.info("Processing %d pattern outputs in original order", len(ordered_outputs))

        # Process outputs strictly in the original order they were defined in the pattern
        # This ensures we follow the pattern definition order exactly
        display_content = None
        collected_display_outputs = []

        # Emergency fallback check - if we have a website generation pattern but no HTML content,
        # try one last aggressive extraction from the raw response
        website_pattern = any(output.output_type == OutputType.HTML for output in pattern_outputs)
        # Find HTML output if it exists
        html_output = next(
            (output for output in pattern_outputs if output.output_type == OutputType.HTML),
            None
        )

        # Check if emergency extraction is needed for website patterns
        needs_extraction = (
            website_pattern and html_output and
            not html_output.get_content() and
            isinstance(response, dict) and 'content' in response
        )
        if needs_extraction:
            logger.warning("Website pattern detected but HTML content missing - trying emergency extraction")
            # Extract content as string from response
            if isinstance(response, dict) and 'content' in response:
                content_value = response['content']
                raw_content = content_value if isinstance(content_value, str) else str(content_value)
            else:
                raw_content = str(response)

            # Try to find HTML content
            # Pattern to match complete HTML documents
            html_pattern = r'<!DOCTYPE html>[\s\S]*?<html[\s\S]*?<body[\s\S]*?</body>[\s\S]*?</html>'
            html_match = re.search(html_pattern, raw_content, re.IGNORECASE)
            if html_match:
                # Get the HTML content and clean up escaped characters
                html_content = html_match.group(0)
                html_content = self._clean_escaped_content(html_content)

                # Make sure html_output is not None before setting content
                if html_output:
                    html_output.set_content(html_content)
                    logger.info("Emergency HTML content extraction successful")
                else:
                    logger.warning("HTML output object is None, cannot set content")

                # Also try to find CSS and JS content
                # Find CSS output if it exists
                css_output = next(
                    (output for output in pattern_outputs if output.output_type == OutputType.CSS),
                    None
                )
                if css_output and not css_output.get_content():
                    css_match = re.search(r'```css\s*([\s\S]*?)\s*```', raw_content, re.DOTALL)
                    if css_match:
                        css_content = css_match.group(1)
                        css_content = self._clean_escaped_content(css_content)
                        css_output.set_content(css_content)
                        logger.info("Emergency CSS content extraction successful")

                # Find JS output if it exists
                js_output = next(
                    (output for output in pattern_outputs if output.output_type == OutputType.JS),
                    None
                )
                if js_output and not js_output.get_content():
                    # Pattern to match JavaScript code blocks
                    js_pattern = r'```(?:js|javascript)\s*([\s\S]*?)\s*```'
                    js_match = re.search(js_pattern, raw_content, re.DOTALL)
                    if js_match:
                        js_content = js_match.group(1)
                        js_content = self._clean_escaped_content(js_content)
                        js_output.set_content(js_content)
                        logger.info("Emergency JS content extraction successful")

        # Process each output in the exact order defined in the pattern
        for output in ordered_outputs:
            content = output.get_content()
            # Log output processing details
            logger.info(
                "Processing output: %s, type: %s, action: %s",
                output.name, output.output_type, output.action
            )

            # Process based on action type
            if output.action == OutputAction.DISPLAY:
                if output.output_type == OutputType.MARKDOWN:
                    # Clean up any whitespace or unwanted characters
                    content = content.strip()

                    # Format the markdown content
                    display_content = self.formatters['console'].format(
                        content,
                        content_type='markdown'
                    )
                    # Print the display content immediately before executing any commands
                    print(display_content)
                    # Also store for return value
                    collected_display_outputs.append(display_content)
                    logger.info("Displayed markdown content for '%s'", output.name)
                elif output.output_type == OutputType.TEXT:
                    display_content = self.formatters['console'].format(content, content_type='text')
                    print(display_content)
                    collected_display_outputs.append(display_content)
                    logger.info("Displayed text content for '%s'", output.name)
                else:
                    display_content = self.formatters['console'].format(content)
                    print(display_content)
                    collected_display_outputs.append(display_content)
                    logger.info("Displayed generic content for '%s'", output.name)

            # Execute commands in order
            elif output.action == OutputAction.EXECUTE:
                logger.info("Executing command: %s", output.name)
                PatternOutput.execute_command(content, output.name)

            # Process file writes in order
            elif output.action == OutputAction.WRITE:
                content = output.get_content()
                logger.info("Processing write output: %s", output.name)
                if output.write_to_file and output_dir:
                    file_path = os.path.join(output_dir, output.write_to_file)
                    try:
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)

                        # Check if content exists
                        if content is None:
                            logger.warning("No content found for %s, skipping file write", output.name)
                            continue

                        # Handle content size
                        content_size = len(str(content)) if content else 0
                        if content_size > 1000000:  # 1MB
                            logger.warning("Very large content (%.2fMB) for %s", content_size/1000000, output.name)

                        # Ensure content is a string
                        if not isinstance(content, str):
                            if isinstance(content, (dict, list)):
                                try:
                                    content = json.dumps(content, indent=2)
                                except Exception as je:
                                    logger.error("Error converting JSON: %s", str(je))
                                    content = str(content)  # Fallback to simple string representation
                            else:
                                content = str(content)

                        # Clean content for specific output types that might have problematic characters
                        if output.output_type in [OutputType.HTML, OutputType.CSS, OutputType.JS]:
                            # Remove any null bytes or other problematic characters
                            content = content.replace('\x00', '')

                            # Check for and remove leading/trailing code block markers
                            if output.output_type == OutputType.HTML:
                                content = re.sub(r'^```html\s*', '', content)
                            elif output.output_type == OutputType.CSS:
                                content = re.sub(r'^```css\s*', '', content)
                            elif output.output_type == OutputType.JS:
                                content = re.sub(r'^```js\s*|^```javascript\s*', '', content)

                            content = re.sub(r'\s*```$', '', content)

                        # Log content type information
                        logger.info("Writing file to %s", file_path)
                        logger.info("Content type: %s (%s)", output.name, output.output_type)
                        logger.debug("First 100 chars of content: %s", content[:100])

                        # Write to file using the file writer
                        success = self.file_writer.write_by_extension(content, file_path)
                        if success:
                            created_files.append(file_path)
                            logger.info("Write success: %s", success)
                            logger.info("Saved %s to %s", output.name, file_path)
                        else:
                            logger.error("Failed to write %s to %s", output.name, file_path)

                            # Try direct file write as a fallback
                            try:
                                logger.info("Attempting direct file write as fallback")
                                with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
                                    f.write(content)
                                logger.info("Direct file write succeeded for %s", file_path)
                                created_files.append(file_path)
                            except Exception as dw_err:
                                logger.error("Direct file write also failed: %s", str(dw_err))
                    except Exception as e:
                        logger.error("Error writing output %s to file: %s", output.name, str(e))
                        logger.debug("Error details: %s", traceback.format_exc())
                        # Combine all display outputs to return (or use the first one if there are multiple)
        if collected_display_outputs:
            visual_content = "\n\n".join(collected_display_outputs)

        # If we still don't have visual content, try to use the raw response for debugging
        if not visual_content:
            logger.debug("No processed visual content found, trying alternative approaches")

            # Check if the response itself is already a properly formatted JSON
            if isinstance(response, dict) and 'results' in response:
                logger.debug("Response is already a JSON with results field")
                results = response['results']
                if 'explanation' in results and isinstance(results['explanation'], str):
                    logger.debug("Using explanation from results directly")
                    markdown_content = results['explanation']
                    visual_content = self.formatters['console'].format(markdown_content, content_type='markdown')

                    # Handle the command execution as well if it exists
                    if 'command' in results and isinstance(results['command'], str):
                        logger.debug("Found command in results, executing")
                        command = results['command']
                        PatternOutput.execute_command(command, "command")

            # If still no visual content and we have content field, use it
            elif not visual_content and isinstance(response, dict) and 'content' in response:
                logger.debug("Falling back to raw response content")
                raw_content = response['content']
                if isinstance(raw_content, str) and raw_content.strip():
                    # Check if content contains JSON
                    json_match = re.search(r'{.*}', raw_content, re.DOTALL)
                    if json_match:
                        try:
                            # Try to parse the JSON
                            json_content = json.loads(json_match.group(0))
                            if 'results' in json_content:
                                results = json_content['results']
                                if 'explanation' in results and isinstance(results['explanation'], str):
                                    logger.debug("Using explanation from parsed JSON content")
                                    markdown_content = results['explanation']
                                    visual_content = self.formatters['console'].format(
                                        markdown_content, content_type='markdown')

                                    # Handle the command execution as well if it exists
                                    if 'command' in results and isinstance(results['command'], str):
                                        logger.debug("Found command in parsed JSON, executing")
                                        command = results['command']
                                        PatternOutput.execute_command(command, "command")
                                return visual_content or raw_content, created_files
                        except json.JSONDecodeError:
                            logger.debug("Failed to parse JSON in content")

                    # If no JSON or JSON parsing failed, just return the raw content
                    return raw_content, created_files

        # Return the visual content and created files (with more helpful fallback message)
        if not visual_content:
            logger.error("Failed to extract pattern outputs. Structured data keys: %s", list(structured_data.keys()))
            return "Failed to extract pattern outputs. Check the format of the AI response.", created_files

        return visual_content, created_files

    def _extract_output_content_from_response(self,
                                           pattern_outputs: List[PatternOutput],
                                           structured_data: Dict[str, Any],
                                           response: Union[str, Dict]) -> None:
        """Extract content for each pattern output from the response.

        Args:
            pattern_outputs: List of pattern outputs to populate
            structured_data: Structured data extracted from response
            response: Original response from the AI
        """
        # Log what we're working with
        logger.info("Extracting content from structured data with keys: %s", list(structured_data.keys()))

        # If we have an empty structured_data but a dict response, try to use it directly
        if not structured_data and isinstance(response, dict):
            logger.warning("Structured data is empty but response is a dictionary, trying direct extraction")
            if 'content' in response and isinstance(response['content'], str):
                # Try to get the response content
                raw_content = response['content']
                logger.info("Using raw content from response (length: %d)", len(raw_content))

                # Try to extract content using regex patterns
                html_match = re.search(r'```html\s*(.*?)\s*```', raw_content, re.DOTALL)
                css_match = re.search(r'```css\s*(.*?)\s*```', raw_content, re.DOTALL)
                js_match = re.search(r'```(?:js|javascript)\s*(.*?)\s*```', raw_content, re.DOTALL)

                # Add any found matches to structured_data
                if html_match:
                    structured_data['html_content'] = html_match.group(1)
                    logger.info("Extracted HTML content from raw response")

                if css_match:
                    structured_data['css_styles'] = css_match.group(1)
                    logger.info("Extracted CSS content from raw response")

                if js_match:
                    structured_data['javascript_code'] = js_match.group(1)
                    logger.info("Extracted JavaScript content from raw response")

        # Add debugging for empty structured data
        if not structured_data:
            logger.error("Structured data is empty, outputs will not be populated properly")
            # Try to log the response content for debugging
            if isinstance(response, dict) and 'content' in response:
                content_sample = (response['content'][:500] + "..."
                                 if len(response['content']) > 500 else response['content'])
                logger.debug("Response content: %s", content_sample)
            elif isinstance(response, str):
                content_sample = response[:500] + "..." if len(response) > 500 else response
                logger.debug("Response string: %s", content_sample)

        # Process each output definition
        for output in pattern_outputs:
            # Skip if output already has content
            if output.get_content() is not None:
                continue

            content = None
            logger.info("Looking for content for output: %s", output.name)

            # Step 1: Direct field matching in structured data - this should be the main way
            # to get outputs in the new pattern system
            if output.name in structured_data:
                content = structured_data[output.name]
                logger.info("Found direct match for %s in structured data", output.name)

            # Step 2: Type-based field matching for common field names
            elif not content:
                if output.output_type == OutputType.HTML and "html_content" in structured_data:
                    content = structured_data["html_content"]
                    logger.info("Found html_content match based on output type")

                elif output.output_type == OutputType.CSS and "css_styles" in structured_data:
                    content = structured_data["css_styles"]
                    logger.info("Found css_styles match based on output type")

                elif output.output_type == OutputType.JS and (
                    "javascript_code" in structured_data or "script" in structured_data
                ):
                    content = structured_data.get("javascript_code") or structured_data.get("script")
                    logger.info("Found javascript match based on output type")

            # Step 3: Extract from code blocks by language (last resort)
            if not content:
                language_map = {
                    OutputType.HTML: "html",
                    OutputType.CSS: "css",
                    OutputType.JS: "js",
                    OutputType.MARKDOWN: "markdown",
                    OutputType.CODE: "code",
                    OutputType.JSON: "json",
                    OutputType.TEXT: "text",
                }
                language = language_map.get(output.output_type)

                # First try to extract from response string
                if language and isinstance(response, str):
                    content = self._extract_from_code_blocks(response, language)
                    if content:
                        logger.info("Extracted %s from code block of type %s in direct response", output.name, language)

                # If that fails, try to extract from the content field if available
                if (not content and language and isinstance(response, dict)
                        and 'content' in response and isinstance(response['content'], str)):
                    content = self._extract_from_code_blocks(response['content'], language)
                    if content:
                        logger.info("Extracted %s from code block of type %s in response content",
                                    output.name, language)

            # Step 4: For website generation, try searching for common patterns if still not found
            if not content and output.output_type in [OutputType.HTML, OutputType.CSS, OutputType.JS]:
                logger.info("Trying fallback pattern extraction for %s", output.name)
                content = self._extract_content_by_patterns(response, output.output_type)
                if content:
                    logger.info("Found content for %s using pattern extraction", output.name)

            # If content found, set it
            if content is not None:
                # Ensure proper content handling based on output type
                if output.output_type == OutputType.MARKDOWN and isinstance(content, str):
                    # Make sure markdown content is properly formatted
                    output.set_content(content)
                    logger.info("Set content for %s (MARKDOWN, length: %d)", output.name, len(content))
                else:
                    output.set_content(content)
                    content_len = len(content) if isinstance(content, str) else "N/A"
                    logger.info("Set content for %s (type: %s, length: %s)",
                               output.name, output.output_type, content_len)
            else:
                logger.error("No content found for output %s - will have empty output", output.name)

    def _extract_content_by_patterns(
            self,
            response: Union[str, Dict],
            output_type: OutputType
    ) -> Optional[str]:
        """Extract content from response using common patterns for web content.

        This is a more aggressive fallback method when regular extraction fails.

        Args:
            response: The AI response
            output_type: Type of output to extract

        Returns:
            Optional[str]: Extracted content or None if not found
        """
        # Extract the string content to search in
        content_to_search = ""
        if isinstance(response, str):
            content_to_search = response
        elif isinstance(response, dict) and 'content' in response:
            content_to_search = (response['content'] if isinstance(response['content'], str)
                                else str(response['content']))
        else:
            # Try to convert entire response to string as last resort
            try:
                content_to_search = str(response)
            except Exception as e:
                logger.error("Failed to convert response to string: %s", str(e))
                return None

        # Early return if no content
        if not content_to_search:
            return None

        try:
            # Different patterns based on output type
            if output_type == OutputType.HTML:
                # Pattern 1: Look for complete HTML documents
                html_pattern = r'<!DOCTYPE html>[\s\S]*?<html[\s\S]*?<head[\s\S]*?<body[\s\S]*?</body>[\s\S]*?</html>'
                match = re.search(html_pattern, content_to_search, re.IGNORECASE)
                if match:
                    return match.group(0)

                # Pattern 2: Look for HTML fragments with tags
                html_fragment = r'<div[\s\S]*?</div>|<section[\s\S]*?</section>'
                matches = re.findall(html_fragment, content_to_search, re.IGNORECASE)
                if matches and len(matches[0]) > 50:  # Make sure it's substantial
                    return matches[0]

            elif output_type == OutputType.CSS:
                # Pattern 1: Look for CSS rule blocks
                css_pattern = r'(\w+(?:\s*,\s*\w+)*\s*\{[\s\S]*?\})'
                matches = re.findall(css_pattern, content_to_search)
                if matches:
                    # Combine multiple CSS rules
                    return '\n\n'.join(matches)

                # Pattern 2: Look for anything that looks like CSS
                css_simple = r'([\w\s\.\#\-]+\s*\{[^}]*\})'
                matches = re.findall(css_simple, content_to_search)
                if matches:
                    return '\n\n'.join(matches)

            elif output_type == OutputType.JS:
                # Pattern 1: Look for complete JS blocks
                js_patterns = [
                    r'document\.addEventListener\([\'"]DOMContentLoaded[\'"]\s*,\s*function\s*\([^)]*\)'
                    r'\s*\{[\s\S]*?\}\s*\);',
                    r'function\s+\w+\s*\([^)]*\)\s*\{[\s\S]*?\}',
                    r'const\s+\w+\s*=\s*function\s*\([^)]*\)\s*\{[\s\S]*?\}',
                    r'let\s+\w+\s*=\s*\([^)]*\)\s*=>\s*\{[\s\S]*?\}'
                ]

                for pattern in js_patterns:
                    matches = re.findall(pattern, content_to_search)
                    if matches:
                        return '\n\n'.join(matches)

                # Pattern 2: Look for any JavaScript-like code
                js_vars = r'(const|let|var)\s+\w+\s*=\s*[^;]+;'
                matches = re.findall(js_vars, content_to_search)
                if matches and len(''.join(matches)) > 50:
                    return '\n'.join(matches)

            # No suitable content found
            return None

        except Exception as e:
            logger.error("Error in pattern extraction: %s", str(e))
            return None

    def _extract_command_from_response(self, response: Union[str, Dict]) -> Optional[str]:
        """Extract command string from different response formats.

        Args:
            response: The AI response

        Returns:
            Optional[str]: Command string or None if not found
        """
        # Case 1: Direct dictionary with result field
        if isinstance(response, dict) and "result" in response:
            result = response["result"]
            if isinstance(result, str):
                return result.strip()

        # Case 2: Response has content field with embedded JSON
        if isinstance(response, dict) and "content" in response:
            content = response["content"]

            # Try to extract using simple pattern matching
            result_match = re.search(r'"result":\s*"([^"]+)"', content)
            if result_match:
                return result_match.group(1).strip()

            # Look for JSON block in content
            match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
            if match:
                try:
                    json_content = json.loads(match.group(1))
                    if "result" in json_content:
                        return json_content["result"].strip()
                except json.JSONDecodeError:
                    logger.debug("Failed to parse JSON from content block")

        # Case 3: Nested API response format
        if isinstance(response, dict) and "choices" in response and response["choices"]:
            try:
                first_choice = response["choices"][0]
                if isinstance(first_choice, dict) and "message" in first_choice:
                    message = first_choice["message"]
                    if isinstance(message, dict) and "content" in message:
                        content = message["content"]

                        # Look for JSON block in content
                        match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
                        if match:
                            json_content = json.loads(match.group(1))
                            if "result" in json_content:
                                return json_content["result"].strip()
            except Exception as e:
                logger.warning("Error extracting command from response: %s", str(e))

        # Case 4: FALLBACK - Try to find common command patterns in text
        text_content = ""
        if isinstance(response, str):
            text_content = response
        elif isinstance(response, dict):
            if "content" in response:
                text_content = response["content"]
            elif isinstance(response, dict) and "choices" in response and response["choices"]:
                first_choice = response["choices"][0]
                if isinstance(first_choice, dict) and "message" in first_choice:
                    message = first_choice["message"]
                    if isinstance(message, dict) and "content" in message:
                        text_content = message["content"]

        if text_content:
            # Look for anything that looks like a Linux command in the content
            command_patterns = [
                r'find\s+[.]\s+-type\s+f\s+-size',
                r'ls\s+-[la]+h\s+',
                r'grep\s+-[r]+',
                r'ps\s+aux',
                r'cat\s+[\w/]+',
                r'cp\s+-[r]*\s+[\w/]+\s+[\w/]+',
                r'curl\s+-[a-zA-Z]\s+http'
            ]

            for pattern in command_patterns:
                command_match = re.search(pattern, text_content)
                if command_match:
                    # Extract a reasonable command length
                    start = command_match.start()
                    end = min(start + 100, len(text_content))
                    command_line = text_content[start:end].split('\n')[0]
                    return command_line.strip().strip('"')

        return None

    def _handle_pattern_outputs(self, response: Union[str, Dict], pattern_outputs: List[PatternOutput]) -> List[str]:
        """Handle pattern-defined outputs based on pattern definitions.

        Args:
            response: The AI response
            pattern_outputs: List of pattern outputs

        Returns:
            List[str]: List of created file paths
        """
        created_files = []

        # Extract structured data from response
        structured_data = self._extract_structured_data(response)

        # Get output types
        execute_outputs, display_outputs, file_outputs = self._categorize_outputs(pattern_outputs)

        # Skip if no outputs to process
        if not file_outputs and not display_outputs and not execute_outputs:
            logger.debug("No pattern outputs to process")
            return created_files

        # Get output directory with user confirmation
        output_dir = self._get_output_directory()
        if not output_dir:
            logger.debug("Output directory selection cancelled")
            return created_files

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Extract and populate content for outputs
        self._extract_pattern_contents(pattern_outputs, response, structured_data)

        # Process display outputs separately
        for output in display_outputs:
            if output.get_content():
                # Default to markdown extension for display outputs
                ext = ".md" if output.output_type == OutputType.MARKDOWN else ".txt"
                display_file = os.path.join(output_dir, f"{output.name}{ext}")
                try:
                    content = output.get_content()
                    if content is not None:
                        with open(display_file, 'w', encoding='utf-8') as f:
                            f.write(str(content))
                        created_files.append(display_file)
                        logger.info("Display output '%s' saved to %s", output.name, display_file)
                    else:
                        logger.warning("Cannot save empty content for '%s'", output.name)
                except Exception as e:
                    logger.error("Error saving display output '%s': %s", output.name, str(e))

        # Write each file output to file
        for output in file_outputs:
            content = output.get_content()
            if not content:
                continue

            # Ensure content is a string
            if not isinstance(content, str):
                if isinstance(content, (dict, list)):
                    content = json.dumps(content, indent=2)
                else:
                    content = str(content)

            # Get appropriate file path
            file_path = self._get_output_file_path(output, output_dir)
            if not file_path:
                continue

            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Write to file using the file writer
            success = self.file_writer.write_by_extension(content, file_path)
            if success:
                created_files.append(file_path)
                logger.info("Saved %s to %s", output.name, file_path)
            else:
                logger.error("Failed to write %s to %s", output.name, file_path)

        return created_files

    def _extract_structured_data(self, response: Union[str, Dict]) -> Dict[str, Any]:
        """Extract structured data from response focusing on the new pattern format.

        The new pattern format expects a 'results' object containing named outputs.
        This method extracts this structure from various response formats.

        Args:
            response: The AI response

        Returns:
            Dict: Extracted structured data from the 'results' object
        """
        # Log incoming response type for debugging
        if isinstance(response, dict):
            logger.debug("Response type: dictionary with keys %s", list(response.keys()))
        else:
            logger.debug("Response type: %s", type(response))

        # Initialize empty result
        result_data = {}

        # Handle dictionary response
        if isinstance(response, dict):
            # Log response size to help diagnose large response issues
            if 'content' in response and isinstance(response['content'], str):
                content_size = len(response['content'])
                logger.debug("Response content size: %d characters", content_size)
                if content_size > 1000000:  # 1MB
                    logger.warning("Very large content detected: %.2fMB", content_size/1000000)

            # Case 1: Standard format with a 'results' object
            if 'results' in response and isinstance(response['results'], dict):
                logger.debug("Found 'results' key with keys: %s", list(response['results'].keys()))
                # Make a deep copy to prevent any potential reference issues
                try:
                    result_data = dict(response['results'])
                    return result_data
                except Exception as e:
                    logger.error("Error copying results data: %s", str(e))
                    # Fall back to direct reference if copying fails
                    return response['results']

            # Case 2: Keys without a 'results' wrapper - see if they match pattern output names
            # This could happen if the AI didn't wrap outputs in 'results' object
            # Filter out common API response keys that aren't actual results
            common_api_keys = {'content', 'choices', 'message', 'model', 'id', 'finish_reason',
                             'created', 'usage', 'usage_tokens', 'response_id'}

            potential_output_keys = {k: v for k, v in response.items()
                                   if k not in common_api_keys and not k.startswith('_')}

            if len(potential_output_keys) > 0:
                logger.debug("Found potential direct output fields: %s", list(potential_output_keys.keys()))
                return potential_output_keys

            # Case 3: API response with nested content field
            if 'content' in response and isinstance(response['content'], str):
                # Try to extract JSON from content
                content_data = self._extract_json_from_text(response['content'])
                if content_data and isinstance(content_data, dict):
                    if 'results' in content_data and isinstance(content_data['results'], dict):
                        return content_data['results']
                    # Check if content_data directly contains output fields
                    # (AI might have forgotten to use 'results' wrapper)
                    potential_output_keys = {k: v for k, v in content_data.items()
                                         if k not in common_api_keys and not k.startswith('_')}
                    if len(potential_output_keys) > 0:
                        logger.debug("Found potential output fields in content: %s",
                                   list(potential_output_keys.keys()))
                        return potential_output_keys

            # Case 4: API response format with choices
            elif 'choices' in response and isinstance(response['choices'], list) and response['choices']:
                for choice in response['choices']:
                    if isinstance(choice, dict) and 'message' in choice and 'content' in choice['message']:
                        content_data = self._extract_json_from_text(choice['message']['content'])
                        if content_data and isinstance(content_data, dict):
                            if 'results' in content_data and isinstance(content_data['results'], dict):
                                return content_data['results']
                            # Check for direct output fields
                            potential_output_keys = {k: v for k, v in content_data.items()
                                                  if k not in common_api_keys and not k.startswith('_')}
                            if len(potential_output_keys) > 0:
                                return potential_output_keys

        # Handle string response
        elif isinstance(response, str):
            content_data = self._extract_json_from_text(response)
            if content_data and isinstance(content_data, dict):
                if 'results' in content_data and isinstance(content_data['results'], dict):
                    return content_data['results']
                # Check for direct output fields
                common_api_keys = {'content', 'choices', 'message', 'model', 'id'}
                potential_output_keys = {k: v for k, v in content_data.items()
                                      if k not in common_api_keys and not k.startswith('_')}
                if len(potential_output_keys) > 0:
                    logger.debug("Found potential output fields in JSON string: %s",
                               list(potential_output_keys.keys()))
                    return potential_output_keys

        # If we couldn't find a properly structured 'results' object, return empty dict
        logger.debug("No 'results' object found in response, returning empty dict")
        return {}

    def _extract_json_from_text(self, text: str) -> Optional[Dict]:
        """Extract JSON from text, looking in code blocks or trying to parse the entire text.

        Args:
            text: Text to extract JSON from

        Returns:
            Optional[Dict]: Extracted JSON data or None if not found
        """
        if not text or not isinstance(text, str):
            return None

        logger.debug("Extracting JSON from text: %s...", text[:100])

        # First try to parse the entire text as JSON directly - it might be pure JSON
        try:
            # Check if the whole text is valid JSON
            if text.strip().startswith('{') and text.strip().endswith('}'):
                parsed_json = json.loads(text)
                logger.debug("Successfully parsed entire text as JSON")
                return parsed_json
        except json.JSONDecodeError:
            logger.debug("Full text is not valid JSON, trying other methods")

        # Try to extract JSON from code blocks
        try:
            # Look for code blocks with JSON content
            json_match = re.search(r'```(?:json)?(.*?)```', text, re.DOTALL)
            if json_match:
                json_content = json_match.group(1).strip()
                # Check if content looks like JSON
                if json_content and (json_content.startswith('{') or json_content.startswith('[')):
                    logger.debug("Found JSON in code block: %s...", json_content[:100])
                    parsed_json = json.loads(json_content)
                    return parsed_json
        except (json.JSONDecodeError, re.error) as e:
            logger.debug("Failed to parse JSON from code block: %s", str(e))

        # Look for JSON content with ```json followed by content followed by ```
        try:
            improved_json_match = re.search(r'```json(.*?)```', text, re.DOTALL)
            if improved_json_match:
                json_content = improved_json_match.group(1).strip()
                if json_content.startswith('{') or json_content.startswith('['):
                    parsed_json = json.loads(json_content)
                    logger.debug("Found and parsed JSON from code block with improved regex")
                    return parsed_json
        except (json.JSONDecodeError, re.error) as e:
            logger.debug("Failed to parse JSON with improved regex: %s", str(e))

        # Try to find JSON-like structure with curly braces
        try:
            # Use a more comprehensive pattern to capture the entire JSON object
            simple_json_pattern = r'(\{.*?\})'
            matches = re.finditer(simple_json_pattern, text, re.DOTALL)

            for match in matches:
                try:
                    potential_json = match.group(1)
                    logger.debug("Found potential JSON: %s...", potential_json[:100])
                    parsed_json = json.loads(potential_json)

                    # Only return if it's actually a dictionary with data
                    if isinstance(parsed_json, dict) and parsed_json:
                        # Check if it has a 'results' key, which is our expected format
                        if 'results' in parsed_json:
                            logger.debug("Found JSON-like structure with 'results' key in text")
                            return parsed_json
                        # Even if there's no 'results' key, the JSON might be directly usable
                        logger.debug("Found JSON-like structure, but no 'results' key")
                        if any(key in parsed_json for key in ['command', 'explanation', 'output']):
                            logger.debug("JSON has useful keys, using directly")
                            return {'results': parsed_json}
                except json.JSONDecodeError:
                    logger.debug("Failed to parse potential JSON: %s...", potential_json[:50])
                    continue
        except re.error:
            logger.debug("Error in regex pattern for JSON extraction")

        # Last resort: try to parse the entire text as JSON
        try:
            parsed_json = json.loads(text)
            if isinstance(parsed_json, dict):
                logger.debug("Parsed entire text as JSON")
                return parsed_json
        except json.JSONDecodeError:
            logger.debug("Text is not valid JSON")

        return None
    def _categorize_outputs(self, pattern_outputs: List[PatternOutput]) -> Tuple[
        List[PatternOutput], List[PatternOutput], List[PatternOutput]
    ]:
        """Categorize pattern outputs by action type.

        Args:
            pattern_outputs: List of pattern outputs

        Returns:
            Tuple: (execute_outputs, display_outputs, file_outputs)
        """
        if not pattern_outputs:
            return [], [], []

        # Categorize outputs by action
        execute_outputs = [output for output in pattern_outputs if output.action == OutputAction.EXECUTE]
        display_outputs = [output for output in pattern_outputs if output.action == OutputAction.DISPLAY]
        file_outputs = [output for output in pattern_outputs if output.action == OutputAction.WRITE]

        return execute_outputs, display_outputs, file_outputs

    def _extract_pattern_contents(self,
                               pattern_outputs: List[PatternOutput],
                               response: Union[str, Dict],
                               structured_data: Dict[str, Any]) -> None:
        """Extract and set content for all pattern outputs.

        Args:
            pattern_outputs: List of pattern outputs
            response: The original AI response
            structured_data: Extracted structured data
        """
        # Direct extraction for fields in structured data
        for output in pattern_outputs:
            # Check if already has content
            if output.get_content() is not None:
                continue

            # Try to extract content from response
            content = None

            # Method 1: Direct lookup in structured data by name
            if output.name in structured_data:
                content = structured_data[output.name]
                logger.debug("Found direct match for %s in structured data", output.name)

            # Method 2: Type-based content extraction for common field names
            elif not content:
                type_field_mappings = {
                    OutputType.HTML: ["html_content", "html"],
                    OutputType.CSS: ["css_styles", "css", "stylesheet"],
                    OutputType.JS: ["javascript_code", "script", "js"],
                    OutputType.TEXT: ["text_content", "plain_text"],
                    OutputType.MARKDOWN: ["markdown_content", "md"],
                    OutputType.JSON: ["json_content", "data"],
                    OutputType.CODE: ["code", "command", "query"]
                }

                if output.output_type in type_field_mappings:
                    for field_name in type_field_mappings[output.output_type]:
                        if field_name in structured_data:
                            content = structured_data[field_name]
                            logger.debug("Found content for %s in %s field", output.name, field_name)
                            break

            # Method 3: Extract from code blocks by output type as a last resort
            if not content and isinstance(response, str):
                content = self._extract_from_code_blocks(response, output.output_type.value)
                if content:
                    logger.debug("Extracted %s from code block", output.name)

            # If content found, set it
            if content is not None:
                output.set_content(content)
                logger.debug("Set content for output %s", output.name)
            else:
                logger.debug("No content found for output %s", output.name)

    def _extract_from_code_blocks(self, text: str, language: str) -> Optional[str]:
        """Extract content from markdown code blocks.

        Args:
            text: Text to search
            language: Code block language identifier

        Returns:
            Optional[str]: Extracted content or None
        """
        if not isinstance(text, str):
            return None

        try:
            # Record original text size for debugging
            text_size = len(text)
            logger.debug("Extracting %s code blocks from %d character text", language, text_size)

            # Build more robust patterns for different language formats
            language_variations = [language, language.lower(), language.capitalize()]
            if language.lower() == 'javascript':
                language_variations.append('js')
            elif language.lower() == 'js':
                language_variations.append('javascript')
            elif language.lower() == 'markdown':
                language_variations.append('md')
            elif language.lower() == 'md':
                language_variations.append('markdown')

            # First look for code blocks with the exact language
            for lang_variation in language_variations:
                # More robust pattern to handle various code block formats
                pattern = rf'```\s*{lang_variation}\s*\n([\s\S]*?)\n```'
                matches = re.finditer(pattern, text, re.IGNORECASE)

                for match in matches:
                    content = match.group(1).strip()
                    if content:
                        logger.debug("Found %s code block with %d chars", lang_variation, len(content))
                        # Clean escaped content
                        return re.sub(r'\\([`\'"])', r'\1', content)

            # If no specific language blocks found, try without language identifier
            pattern = r'```\s*\n([\s\S]*?)\n```'
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                content = match.group(1).strip()
                if content:
                    logger.debug("Found generic code block with %d chars", len(content))
                    # Clean escaped content
                    return re.sub(r'\\([`\'"])', r'\1', content)

            # Also look for generic code blocks within language-specific sections
            section_pattern = rf'##\s+{language}.*?\n([\s\S]*?)(?=##|\Z)'
            section_matches = re.finditer(section_pattern, text, re.IGNORECASE)

            for match in section_matches:
                section = match.group(1)
                code_match = re.search(r'```([\s\S]*?)```', section, re.DOTALL)
                if code_match:
                    content = code_match.group(1).strip()
                    if content:
                        logger.debug("Found code block in %s section with %d chars", language, len(content))
                        return content

        except Exception as e:
            logger.error("Error extracting code blocks: %s", str(e))
            logger.debug("Traceback: %s", traceback.format_exc())

        return None

    def _clean_escaped_content(self, content: str) -> str:
        """Clean up escaped characters in content.

        Args:
            content: Content to clean

        Returns:
            str: Cleaned content
        """
        if not isinstance(content, str):
            return str(content)

        # Use the same approach as the unified file writer
        cleaned = content.replace('\\n', '\n')
        cleaned = cleaned.replace('\\"', '"')
        cleaned = cleaned.replace("\\'", "'")
        cleaned = cleaned.replace('\\\\', '\\')
        cleaned = cleaned.replace('\\t', '\t')
        cleaned = cleaned.replace('\\r', '\r')
        cleaned = cleaned.replace('\\\n', '\n')

        # Remove JSON-style unicode escapes
        cleaned = re.sub(r'\\u([0-9a-fA-F]{4})',
                         lambda m: chr(int(m.group(1), 16)),
                         cleaned)

        return cleaned

    def _get_output_file_path(self, output: PatternOutput, output_dir: str) -> Optional[str]:
        """Get appropriate file path for an output.

        Args:
            output: The pattern output
            output_dir: Base output directory

        Returns:
            Optional[str]: File path or None
        """
        if not output.write_to_file:
            return None

        # Get filename from pattern output
        filename = output.write_to_file
        output_type = output.output_type.value

        # Special cases for web files
        if output_type == "html" and filename == "index.html":
            return os.path.join(output_dir, filename)
        if output_type == "css":
            css_dir = os.path.join(output_dir, "css")
            os.makedirs(css_dir, exist_ok=True)
            return os.path.join(css_dir, filename)
        if output_type == "js":
            js_dir = os.path.join(output_dir, "js")
            os.makedirs(js_dir, exist_ok=True)
            return os.path.join(js_dir, filename)

        # General case - use the provided filename
        return os.path.join(output_dir, filename)

    def _get_output_directory(self) -> Optional[str]:
        """Get output directory with user confirmation if needed.

        Returns:
            Optional[str]: Output directory path or None if cancelled
        """
        # Use configured directory if available
        if self.output_dir:
            return self.output_dir

        # Prompt user for directory
        print("\n📁 File Output Location")
        print("=" * 50)
        print("The system will create files automatically.")
        print("Hint: Use '.' for current directory or specify a path like './my-website'")

        try:
            directory = input("Enter directory path (or 'cancel' to skip file creation): ").strip()

            if directory.lower() == 'cancel':
                return None

            # Default to current directory
            if not directory:
                directory = "."

            # Resolve path
            directory_path = Path(os.path.expanduser(directory))

            # Check if directory exists
            if directory_path.exists():
                if directory_path.is_dir():
                    return str(directory_path.resolve())
                print(f"❌ '{directory}' exists but is not a directory. Using current directory instead.")
                return str(Path(".").resolve())

            # Confirm directory creation
            print(f"📂 Directory '{directory}' does not exist.")
            create = input("Create this directory? (y/n): ").strip().lower()
            if create in ['y', 'yes', '']:
                os.makedirs(directory_path, exist_ok=True)
                return str(directory_path.resolve())

            print("Using current directory instead.")
            return str(Path(".").resolve())

        except (KeyboardInterrupt, EOFError) as e:
            logger.warning("Input interrupted: %s", str(e))
            print("\nUsing current directory for output.")
            return str(Path(".").resolve())
