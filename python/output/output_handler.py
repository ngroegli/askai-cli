import os
import json
import re
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any, Union, Callable

from patterns.pattern_outputs import PatternOutput, OutputType
from utils import print_error_or_warnings
from .extractors.html_extractor import HtmlExtractor
from .extractors.css_extractor import CssExtractor
from .extractors.js_extractor import JsExtractor
from .extractors.json_extractor import JsonExtractor
from .extractors.markdown_extractor import MarkdownExtractor
from .formatters.console_formatter import ConsoleFormatter
from .formatters.markdown_formatter import MarkdownFormatter

logger = logging.getLogger(__name__)

class OutputHandler:
    """
    Responsible for processing AI outputs and handling all output actions.
    
    This class processes output from the AI service, extracts content in various formats,
    formats it for display, and handles writing to files or executing commands.
    """
    def __init__(self, output_dir: str = None):
        """Initialize the OutputHandler with optional output directory.
        
        Args:
            output_dir: Directory for saving output files
        """
        self.output_dir = output_dir
        
        # Initialize extractors for different content types
        self.extractors = {
            'html': HtmlExtractor(),
            'css': CssExtractor(),
            'js': JsExtractor(),
            'json': JsonExtractor(),
            'markdown': MarkdownExtractor()
        }
        
        # Initialize formatters
        self.formatters = {
            'console': ConsoleFormatter(),
            'markdown': MarkdownFormatter()
        }
    
    def process_output(self, 
                      response: Union[str, Dict], 
                      output_config: Optional[Dict[str, Any]] = None,
                      console_output: bool = True,
                      file_output: bool = False,
                      pattern_outputs: Optional[List[PatternOutput]] = None) -> Tuple[str, List[str]]:
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
        # Handle executable commands first if present
        if pattern_outputs:
            cmd_result = self._handle_command_execution(response, pattern_outputs)
            if cmd_result:
                return cmd_result
        
        # Get normalized string representation of response (preserving original)
        response_text = self._normalize_response(response)
        
        # For pattern-defined outputs with file writing
        if pattern_outputs and file_output:
            created_files = self._handle_pattern_outputs(response, pattern_outputs)
            if created_files:
                # Format response for console if needed
                formatted_output = response
                if console_output:
                    formatted_output = self.formatters['console'].format(response_text)
                return formatted_output, created_files
        
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
            elif 'text' in response:
                return response['text']
            elif 'message' in response:
                return response['message']
            # API formats with nested choices
            elif 'choices' in response and isinstance(response['choices'], list) and response['choices']:
                for choice in response['choices']:
                    if isinstance(choice, dict):
                        if 'message' in choice and 'content' in choice['message']:
                            return choice['message']['content']
                        elif 'text' in choice:
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
                formatted_output = self.formatters['markdown'].format(response_text, content_type='markdown')
            else:
                formatted_output = self.formatters['console'].format(response_text)
        
        return formatted_output, created_files
    
    def _extract_and_save_content(self, 
                               response: Union[str, Dict],
                               response_text: str, 
                               output_config: Dict[str, Any]) -> List[str]:
        """Extract and save different types of content from the response.
        
        Args:
            response: The original AI response
            response_text: Normalized text representation
            output_config: Output configuration
            
        Returns:
            List[str]: List of created file paths
        """
        created_files = []
        
        # Extract and save HTML content
        html_content = self.extractors['html'].extract(response_text)
        if html_content:
            html_filename = output_config.get('html_filename', 'output.html')
            file_path = self._write_to_file(html_content, html_filename)
            if file_path:
                created_files.append(file_path)
                logger.info(f"HTML content saved to {file_path}")
        
        # Extract and save CSS content
        css_content = self.extractors['css'].extract(response)
        if css_content:
            css_filename = output_config.get('css_filename', 'styles.css')
            file_path = self._write_to_file(css_content, css_filename)
            if file_path:
                created_files.append(file_path)
                logger.info(f"CSS content saved to {file_path}")
        
        # Extract and save JavaScript content
        js_content = self.extractors['js'].extract(response)
        if js_content:
            js_filename = output_config.get('js_filename', 'script.js')
            file_path = self._write_to_file(js_content, js_filename)
            if file_path:
                created_files.append(file_path)
                logger.info(f"JavaScript content saved to {file_path}")
        
        # Extract and save JSON content
        json_content = self.extractors['json'].extract(response)
        if json_content:
            json_filename = output_config.get('json_filename', 'data.json')
            json_str = json.dumps(json_content, indent=2) if isinstance(json_content, (dict, list)) else str(json_content)
            file_path = self._write_to_file(json_str, json_filename)
            if file_path:
                created_files.append(file_path)
                logger.info(f"JSON content saved to {file_path}")
        
        # Extract and save Markdown content
        markdown_content = self.extractors['markdown'].extract(response_text)
        if markdown_content:
            markdown_filename = output_config.get('markdown_filename', 'output.md')
            file_path = self._write_to_file(markdown_content, markdown_filename)
            if file_path:
                created_files.append(file_path)
                logger.info(f"Markdown content saved to {file_path}")
        
        return created_files
    
    def _write_to_file(self, content: str, filename: str, subdirectory: str = None) -> Optional[str]:
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
            # Create base output directory
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Handle subdirectory if provided
            if subdirectory:
                dir_path = os.path.join(self.output_dir, subdirectory)
                os.makedirs(dir_path, exist_ok=True)
                file_path = os.path.join(dir_path, filename)
            else:
                file_path = os.path.join(self.output_dir, filename)
            
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return file_path
        except Exception as e:
            logger.error(f"Error writing to file {filename}: {str(e)}")
            return None
    
    def _handle_command_execution(self, 
                               response: Union[str, Dict], 
                               pattern_outputs: List[PatternOutput]) -> Optional[Tuple[str, List[str]]]:
        """Handle executable command patterns.
        
        Args:
            response: The AI response
            pattern_outputs: List of pattern outputs
            
        Returns:
            Optional[Tuple[str, List[str]]]: Result if command executed, None otherwise
        """
        # Find result output configured for execution
        result_output = next((output for output in pattern_outputs 
                          if output.name == "result" and output.should_prompt_for_execution()), None)
        
        if not result_output:
            return None
        
        # Extract command from response
        command = self._extract_command_from_response(response)
        if not command:
            return None
        
        # Get visual output explanation if available
        visual_output = None
        if isinstance(response, dict) and 'visual_output' in response:
            visual_output = response['visual_output']
            if visual_output:
                # Display the visual output explanation
                print("\n" + "=" * 80)
                print(f"COMMAND: {command}")
                print("EXPLANATION:")
                print("=" * 80 + "\n")
                print(visual_output)
        
        # Execute the command
        print(f"\n✅ Executing command: {command}")
        PatternOutput.execute_command(command, result_output.name)
        
        # Return the result to avoid further processing
        return visual_output if visual_output else command, []
    
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
        
        # Case 2: Nested API response format
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
                logger.warning(f"Error extracting command from response: {str(e)}")
        
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
        result_output, visual_output, file_outputs = self._categorize_outputs(pattern_outputs)
        
        # Skip if no outputs to process
        if not file_outputs and not (result_output or visual_output):
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
        
        # Process visual output separately
        if visual_output and visual_output.get_content():
            visual_file = os.path.join(output_dir, "output.md")
            try:
                with open(visual_file, 'w', encoding='utf-8') as f:
                    f.write(visual_output.get_content())
                created_files.append(visual_file)
                logger.info(f"Visual output saved to {visual_file}")
            except Exception as e:
                logger.error(f"Error saving visual output: {str(e)}")
        
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
            
            # Write to file
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                created_files.append(file_path)
                logger.info(f"Saved {output.name} to {file_path}")
            except Exception as e:
                logger.error(f"Error writing output {output.name} to file: {str(e)}")
        
        return created_files
    
    def _extract_structured_data(self, response: Union[str, Dict]) -> Dict[str, Any]:
        """Extract structured data from response.
        
        Args:
            response: The AI response
            
        Returns:
            Dict: Extracted structured data
        """
        # Already a dictionary
        if isinstance(response, dict):
            return response
        
        # Try to parse JSON from string
        if isinstance(response, str):
            try:
                # Look for JSON code blocks
                json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', response)
                if json_match:
                    return json.loads(json_match.group(1))
                
                # Try parsing the entire string as JSON
                return json.loads(response)
            except json.JSONDecodeError:
                pass
        
        # Return empty dict if parsing failed
        return {}
    
    def _categorize_outputs(self, pattern_outputs: List[PatternOutput]) -> Tuple[
        Optional[PatternOutput], Optional[PatternOutput], List[PatternOutput]
    ]:
        """Categorize pattern outputs by type.
        
        Args:
            pattern_outputs: List of pattern outputs
            
        Returns:
            Tuple: (result_output, visual_output, file_outputs)
        """
        if not pattern_outputs:
            return None, None, []
        
        # Find special system fields
        result_output = next((output for output in pattern_outputs 
                           if output.is_system_field and output.name == "result"), None)
                              
        visual_output = next((output for output in pattern_outputs 
                           if output.is_system_field and output.name == "visual_output"), None)
        
        # Find outputs that should be written to files
        file_outputs = [output for output in pattern_outputs if output.should_write_to_file()]
        
        return result_output, visual_output, file_outputs
    
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
            
            # Method 1: Direct lookup in structured data
            if output.name in structured_data:
                content = structured_data[output.name]
            
            # Method 2: Check for common alternative field names
            elif not content and output.output_type == OutputType.HTML and "html_content" in structured_data:
                content = structured_data["html_content"]
            elif not content and output.output_type == OutputType.CSS and "css_styles" in structured_data:
                content = structured_data["css_styles"]
            elif not content and output.output_type == OutputType.JS:
                content = structured_data.get("javascript_code") or structured_data.get("script")
            
            # Method 3: Extract from nested result field
            elif not content and "result" in structured_data and isinstance(structured_data["result"], dict):
                if output.name in structured_data["result"]:
                    content = structured_data["result"][output.name]
            
            # Method 4: Extract from code blocks by output type
            if not content and isinstance(response, str):
                content = self._extract_from_code_blocks(response, output.output_type.value)
            
            # If content found, set it
            if content is not None:
                output.set_content(content)
    
    def _extract_from_code_blocks(self, text: str, language: str) -> Optional[str]:
        """Extract content from markdown code blocks.
        
        Args:
            text: Text to search
            language: Code block language identifier
            
        Returns:
            Optional[str]: Extracted content or None
        """
        # Look for code blocks with the specified language
        pattern = rf'```{language}?\n([\s\S]*?)\n```'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            content = match.group(1).strip()
            return self._clean_escaped_content(content)
        
        # Also look for generic code blocks within language-specific sections
        section_pattern = rf'##\s+{language}.*?\n([\s\S]*?)(?=##|\Z)'
        section_matches = re.finditer(section_pattern, text, re.IGNORECASE)
        
        for match in section_matches:
            section = match.group(1)
            code_match = re.search(r'```([\s\S]*?)```', section, re.DOTALL)
            if code_match:
                content = code_match.group(1).strip()
                # Remove language identifier if present
                content = re.sub(r'^[a-z]+\n', '', content)
                return self._clean_escaped_content(content)
        
        return None
    
    def _clean_escaped_content(self, content: str) -> str:
        """Clean up escaped characters in content.
        
        Args:
            content: Content to clean
            
        Returns:
            str: Cleaned content
        """
        return (content.replace('\\n', '\n')
                      .replace('\\"', '"')
                      .replace('\\\\', '\\')
                      .replace('\\\n', '\n'))
    
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
        elif output_type == "css":
            css_dir = os.path.join(output_dir, "css")
            os.makedirs(css_dir, exist_ok=True)
            return os.path.join(css_dir, filename)
        elif output_type == "js":
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
                else:
                    print(f"❌ '{directory}' exists but is not a directory. Using current directory instead.")
                    return str(Path(".").resolve())
            else:
                # Confirm directory creation
                print(f"📂 Directory '{directory}' does not exist.")
                create = input("Create this directory? (y/n): ").strip().lower()
                if create in ['y', 'yes', '']:
                    os.makedirs(directory_path, exist_ok=True)
                    return str(directory_path.resolve())
                else:
                    print("Using current directory instead.")
                    return str(Path(".").resolve())
                    
        except (KeyboardInterrupt, EOFError) as e:
            logger.warning(f"Input interrupted: {str(e)}")
            print("\nUsing current directory for output.")
            return str(Path(".").resolve())
