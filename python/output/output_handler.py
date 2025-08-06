import os
import json
import re
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any, Union

from patterns.pattern_outputs import PatternOutput, OutputType
from utils import print_error_or_warnings
from .extractors.html_extractor import HtmlExtractor
from .extractors.css_extractor import CssExtractor
from .extractors.js_extractor import JsExtractor
from .extractors.json_extractor import JsonExtractor
from .extractors.markdown_extractor import MarkdownExtractor
from .writers.markdown_writer import MarkdownWriter
from .formatters.console_formatter import ConsoleFormatter
from .formatters.markdown_formatter import MarkdownFormatter

logger = logging.getLogger(__name__)

class OutputHandler:
    """
    Handles the processing and formatting of AI output, extracting
    specific content types and managing their output.
    """
    def __init__(self, output_dir: str = None):
        """
        Initialize the OutputHandler with optional output directory.
        
        Args:
            output_dir (str, optional): Directory for saving output files
        """
        self.output_dir = output_dir
        
        # Initialize extractors
        self.html_extractor = HtmlExtractor()
        self.css_extractor = CssExtractor()
        self.js_extractor = JsExtractor()
        self.json_extractor = JsonExtractor()
        self.markdown_extractor = MarkdownExtractor()
        
        # Initialize writers
        self.markdown_writer = MarkdownWriter(output_dir=output_dir)
        
        # Initialize formatters
        self.console_formatter = ConsoleFormatter()
        self.markdown_formatter = MarkdownFormatter()

    def process_output(self, 
                      output: Union[str, Dict], 
                      output_config: Optional[Dict[str, Any]] = None,
                      console_output: bool = True,
                      file_output: bool = False,
                      pattern_outputs: Optional[List[PatternOutput]] = None) -> Tuple[str, List[str]]:
        """
        Process the AI output based on configuration.
        
        Args:
            output: The raw output from the AI (can be string or dict)
            output_config (Dict, optional): Configuration for output processing
                - format: Format type (rawtext, json, md) from command line args
            console_output (bool): Whether to format for console output
            file_output (bool): Whether to save output to files
            pattern_outputs (List[PatternOutput], optional): Pattern-defined outputs
            
        Returns:
            Tuple[str, List[str]]: The formatted output and list of created files
        """
        # First, check for executable command patterns
        if pattern_outputs:
            cmd_execution_result = self._handle_command_execution(output, pattern_outputs)
            if cmd_execution_result:
                return cmd_execution_result
        
        # Convert dict response to string if needed, while preserving original dict
        output_str = self._normalize_output(output)
        
        # Handle pattern-defined outputs first if provided
        if pattern_outputs and file_output:
            created_files = self._handle_pattern_outputs(output, pattern_outputs)
            if created_files:
                # Format output for console
                formatted_output = output
                if console_output:
                    formatted_output = self.console_formatter.format(output)
                
                return formatted_output, created_files
                
        # Process standard output formats
        return self._process_standard_output(output, output_str, output_config, console_output, file_output)
        
    def _normalize_output(self, output: Union[str, Dict]) -> str:
        """
        Convert different output types to a normalized string representation.
        
        Args:
            output: The raw output from the AI
            
        Returns:
            str: The normalized output string
        """
        if isinstance(output, str):
            return output
            
        if isinstance(output, dict):
            # Try to extract the text content from common API response formats
            if 'content' in output:
                return output['content']
            elif 'text' in output:
                return output['text']
            elif 'message' in output:
                return output['message']
            elif 'choices' in output and output['choices'] and isinstance(output['choices'], list):
                for choice in output['choices']:
                    if isinstance(choice, dict):
                        if 'message' in choice and 'content' in choice['message']:
                            return choice['message']['content']
                        elif 'text' in choice:
                            return choice['text']
            
            # As a last resort, convert the entire dictionary to JSON string
            try:
                return json.dumps(output, indent=2)
            except:
                return str(output)
        
        # Handle other non-string types
        return str(output)
    
    def _handle_command_execution(self, 
                                  output: Union[str, Dict], 
                                  pattern_outputs: List[PatternOutput]) -> Optional[Tuple[str, List[str]]]:
        """
        Check if the output contains an executable command pattern and execute it if found.
        
        Args:
            output: The raw output from the AI
            pattern_outputs: List of PatternOutput objects
            
        Returns:
            Optional[Tuple[str, List[str]]]: Execution result or None if no command was executed
        """
        # Find a "result" output field configured for execution
        result_output = next((output_obj for output_obj in pattern_outputs 
                        if output_obj.name == "result" and output_obj.should_prompt_for_execution()), None)
        
        if not result_output:
            return None
            
        logger.debug("Found pattern with executable result field")
        
        # Extract command from output
        command = self._extract_command(output)
        if not command:
            return None
        
        # Get visual output explanation if available
        visual_content = None
        if isinstance(output, dict) and 'visual_output' in output:
            visual_content = output['visual_output']
            if visual_content:
                # Format output for display
                print("\n" + "=" * 80)
                print(f"COMMAND: {command}")
                print("EXPLANATION:")
                print("=" * 80 + "\n")
                print(visual_content)
        
        # Execute the command
        print(f"\n✅ Executing command: {command}")
        PatternOutput.execute_command(command, result_output.name)
        
        # Return early to avoid further processing
        return visual_content if 'visual_output' in output else command, []
    
    def _extract_command(self, output: Union[str, Dict]) -> Optional[str]:
        """
        Extract a command from different output formats.
        
        Args:
            output: The raw output from the AI
            
        Returns:
            Optional[str]: Extracted command or None if not found
        """
        # Format 1: Direct dictionary with result field
        if isinstance(output, dict) and "result" in output:
            result_value = output["result"]
            if isinstance(result_value, str):
                return result_value.strip()
        
        # Format 2: OpenRouter API response (nested case)
        if isinstance(output, dict) and "choices" in output and output["choices"]:
            first_choice = output["choices"][0]
            if isinstance(first_choice, dict) and "message" in first_choice:
                message = first_choice["message"]
                if isinstance(message, dict) and "content" in message:
                    content = message["content"]
                    
                    # Look for JSON block in content
                    try:
                        match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
                        if match:
                            json_content = json.loads(match.group(1))
                            if "result" in json_content:
                                return json_content["result"].strip()
                    except Exception as e:
                        logger.warning(f"Error parsing JSON from content: {str(e)}")
        
        return None
    
    def _process_standard_output(self, 
                                output: Union[str, Dict],
                                output_str: str,
                                output_config: Optional[Dict[str, Any]], 
                                console_output: bool, 
                                file_output: bool) -> Tuple[str, List[str]]:
        """
        Process standard output formats (HTML, CSS, JS, JSON, Markdown).
        
        Args:
            output: The original raw output
            output_str: The normalized string output
            output_config: Output configuration
            console_output: Whether to format for console output
            file_output: Whether to save output to files
            
        Returns:
            Tuple[str, List[str]]: The formatted output and list of created files
        """
        # Default to empty dict if None
        output_config = output_config or {}
        created_files = []
        
        # Store the format type if it's in the output_config
        output_format = output_config.get('format', 'rawtext')
        
        # Extract and save content for different formats
        if file_output and self.output_dir:
            created_files.extend(self._extract_and_save_content(output, output_str, output_config))
        
        # Format output based on requested format
        formatted_output = output_str
        
        if console_output:
            if output_format == 'md':
                # Use the markdown formatter for MD format
                formatted_output = self.markdown_formatter.format(output_str, content_type='markdown')
            else:
                # Default to console formatter for other formats
                formatted_output = self.console_formatter.format(output_str)
        
        return formatted_output, created_files
    
    def _extract_and_save_content(self, 
                                 output: Union[str, Dict],
                                 output_str: str, 
                                 output_config: Dict[str, Any]) -> List[str]:
        """
        Extract content from output and save to files.
        
        Args:
            output: The original raw output
            output_str: The normalized string output
            output_config: Output configuration
            
        Returns:
            List[str]: List of created file paths
        """
        created_files = []
        
        # Process common content types (HTML, CSS, JS) with a single approach
        content_types = [
            {
                "type": "HTML",
                "extractor": self.html_extractor,
                "source": output_str,  # HTML uses string output
                "config_key": "html_filename",
                "default_filename": "output.html"
            },
            {
                "type": "CSS", 
                "extractor": self.css_extractor,
                "source": output,  # CSS uses original output
                "config_key": "css_filename",
                "default_filename": "styles.css"
            },
            {
                "type": "JavaScript",
                "extractor": self.js_extractor,
                "source": output,  # JS uses original output
                "config_key": "js_filename",
                "default_filename": "script.js"
            }
        ]
        
        # Process each content type with the same logic
        for content_type in content_types:
            content = content_type["extractor"].extract(content_type["source"])
            if content:
                filename = output_config.get(content_type["config_key"], content_type["default_filename"])
                file_path = self._save_to_file(content, filename)
                if file_path:
                    created_files.append(file_path)
                    logger.info(f"{content_type['type']} content saved to {file_path}")
        
        # Extract JSON content
        json_content = self.json_extractor.extract(output)
        if json_content:
            json_filename = output_config.get('json_filename', 'data.json')
            
            # Ensure we have a string for writing
            if isinstance(json_content, dict):
                json_str = json.dumps(json_content, indent=2)
            else:
                json_str = str(json_content)
                
            json_path = self._save_to_file(json_str, json_filename)
            if json_path:
                created_files.append(json_path)
                logger.info(f"JSON content saved to {json_path}")
        
        # Extract Markdown content
        markdown_content = self.markdown_extractor.extract(output_str)
        if markdown_content:
            markdown_filename = output_config.get('markdown_filename', 'output.md')
            markdown_path = self.markdown_writer.write(
                markdown_content, 
                filename=markdown_filename
            )
            if markdown_path:
                created_files.append(markdown_path)
                logger.info(f"Markdown content saved to {markdown_path}")
        
        return created_files
    
    def _save_to_file(self, content: str, filename: str) -> Optional[str]:
        """
        Save content to a file in the output directory.
        
        Args:
            content: The content to save
            filename: The filename to use
            
        Returns:
            Optional[str]: The file path if successful, None otherwise
        """
        if not self.output_dir:
            return None
            
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            file_path = os.path.join(self.output_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return file_path
        except Exception as e:
            logger.error(f"Error saving file {filename}: {str(e)}")
            return None
    
    def _handle_pattern_outputs(self, response: Union[str, Dict], pattern_outputs: List[PatternOutput]) -> List[str]:
        """
        Handle pattern-defined outputs as specified in the pattern markdown file.
        
        Args:
            response: The AI response (either text or dictionary)
            pattern_outputs: List of PatternOutput objects to process
            
        Returns:
            list: A list of created files
        """
        created_files = []
        
        # Extract and prepare data
        json_data = self._extract_json_data(response)
        result_output, visual_output, file_outputs = self._categorize_pattern_outputs(pattern_outputs)
        
        if not file_outputs and not (result_output or visual_output):
            logger.debug("No outputs specified")
            return created_files
        
        # Get the output directory
        output_dir = self._get_output_directory(interactive=True)
        if not output_dir:
            logger.debug("User cancelled output directory selection")
            return created_files
            
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Handle visual output if present
        created_files.extend(self._process_visual_output(visual_output, json_data, output_dir))
        
        # Process command execution via patterns (only if not already handled)
        created_files.extend(self._process_pattern_command(pattern_outputs, response))
        
        # Process file outputs
        created_files.extend(self._process_file_outputs(file_outputs, response, json_data, output_dir))
        
        return created_files
    
    def _extract_json_data(self, response: Union[str, Dict]) -> Dict:
        """
        Extract JSON data from various response formats.
        
        Args:
            response: The AI response
            
        Returns:
            Dict: Extracted JSON data or empty dict if not found
        """
        # If response is already a dictionary, use it directly
        if isinstance(response, dict):
            return response
        
        # Try to extract JSON from string response
        if isinstance(response, str):
            try:
                # Look for JSON object in code block
                match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', response)
                if match:
                    return json.loads(match.group(1))
                
                # Try parsing the entire string
                return json.loads(response)
            except json.JSONDecodeError:
                logger.debug("Could not parse response as JSON")
                pass
        
        # If extraction failed, return empty dict
        return {}
    
    def _categorize_pattern_outputs(self, pattern_outputs: List[PatternOutput]) -> Tuple[
        Optional[PatternOutput], Optional[PatternOutput], List[PatternOutput]
    ]:
        """
        Categorize pattern outputs into result, visual_output and file outputs.
        
        Args:
            pattern_outputs: List of PatternOutput objects
            
        Returns:
            Tuple containing result output, visual output, and file outputs
        """
        if not pattern_outputs:
            return None, None, []
        
        result_output = next((output for output in pattern_outputs 
                            if output.is_system_field and output.name == "result"), None)
                            
        visual_output = next((output for output in pattern_outputs 
                            if output.is_system_field and output.name == "visual_output"), None)
        
        file_outputs = [output for output in pattern_outputs if output.should_write_to_file()]
        
        return result_output, visual_output, file_outputs
    
    def _process_visual_output(self, 
                              visual_output: Optional[PatternOutput], 
                              json_data: Dict, 
                              output_dir: str) -> List[str]:
        """
        Process and save visual output if present.
        
        Args:
            visual_output: The visual output pattern
            json_data: Extracted JSON data
            output_dir: Directory to save output
            
        Returns:
            List[str]: List of created files
        """
        created_files = []
        
        if visual_output and json_data and 'visual_output' in json_data:
            logger.debug("Found visual_output field in response")
            visual_content = json_data['visual_output']
            
            if visual_content:
                visual_file = os.path.join(output_dir, "output.md")
                try:
                    with open(visual_file, 'w', encoding='utf-8') as f:
                        f.write(visual_content)
                    logger.info(f"Visual output saved to {visual_file}")
                    created_files.append(visual_file)
                except Exception as e:
                    logger.error(f"Error saving visual output: {str(e)}")
        
        return created_files
    
    def _process_pattern_command(self, pattern_outputs: List[PatternOutput], response: Union[str, Dict]) -> List[str]:
        """
        Process command execution from pattern outputs.
        
        Args:
            pattern_outputs: List of PatternOutput objects
            response: The AI response
            
        Returns:
            List[str]: List of created files
        """
        # Note: Most command execution is already handled in _handle_command_execution
        # This method handles any remaining special cases
        for output in pattern_outputs:
            # Check for Linux CLI command pattern
            if output.name == "result" and output.output_type.value == "code" and output.auto_run:
                logger.debug("Found pattern output with result field, code type, and auto_run=True")
                
                # Check for result field in response
                if isinstance(response, dict) and 'result' in response:
                    command = response['result']
                    if isinstance(command, str) and command.strip():
                        # Get visual output for explanation
                        visual_content = None
                        if isinstance(response, dict) and 'visual_output' in response:
                            visual_content = response['visual_output']
                            formatted_output = visual_content
                        
                        # Use PatternOutput for execution
                        logger.debug(f"Executing command via PatternOutput: {command}")
                        PatternOutput.execute_command(command, output.name)
                        
                        # Return empty list as we've already handled this output
                        return []
        
        return []
    
    def _process_file_outputs(self, 
                             file_outputs: List[PatternOutput], 
                             response: Union[str, Dict], 
                             json_data: Dict, 
                             output_dir: str) -> List[str]:
        """
        Process and save file outputs.
        
        Args:
            file_outputs: List of file output patterns
            response: The AI response
            json_data: Extracted JSON data
            output_dir: Directory to save outputs
            
        Returns:
            List[str]: List of created files
        """
        created_files = []
        
        # Process standard result field if present
        if 'result' in json_data:
            self._process_result_field(json_data['result'], file_outputs)
        
        # Process API response format
        self._process_openrouter_format(response, file_outputs)
        
        # Write files for each output
        for output in file_outputs:
            content = self._extract_output_content(output, response, json_data)
            if content:
                file_path = self._write_pattern_output(output, content, output_dir)
                if file_path:
                    created_files.append(file_path)
        
        return created_files
    
    def _process_result_field(self, result_data: Any, file_outputs: List[PatternOutput]) -> None:
        """
        Process result field for file outputs.
        
        Args:
            result_data: The result field data
            file_outputs: List of file output patterns
        """
        if isinstance(result_data, dict):
            # Map result data fields to corresponding outputs
            for output in file_outputs:
                if output.name in result_data and output.write_to_file:
                    logger.debug(f"Found {output.name} in result data")
                    setattr(output, 'content', result_data[output.name])
        
        # If result is a single value, assign to first non-visual output
        elif len(file_outputs) == 1 and file_outputs[0].name != "visual_output":
            logger.debug(f"Using single result value for {file_outputs[0].name}")
            setattr(file_outputs[0], 'content', result_data)
    
    def _process_openrouter_format(self, response: Union[str, Dict], file_outputs: List[PatternOutput]) -> None:
        """
        Process OpenRouter API format for file outputs.
        
        Args:
            response: The API response
            file_outputs: List of file output patterns
        """
        if not isinstance(response, dict) or 'choices' not in response:
            return
            
        # Check for standard website output keys
        website_keys = ["html_content", "css_styles", "javascript_code", "visual_output"]
        
        # Process direct output keys
        for key in website_keys:
            if key in response:
                matching_output = next((output for output in file_outputs if output.name == key), None)
                if matching_output:
                    setattr(matching_output, 'content', response[key])
                    logger.debug(f"Found {key} in direct response")
        
        # Check for nested content in OpenRouter format
        try:
            choices = response.get('choices', [])
            if not choices:
                return
                
            first_choice = choices[0]
            if not isinstance(first_choice, dict) or 'message' not in first_choice:
                return
                
            message = first_choice['message']
            if not isinstance(message, dict) or 'content' not in message:
                return
                
            content = message['content']
            if not isinstance(content, str):
                return
                
            # Try to extract JSON from content
            match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', content)
            if not match:
                return
                
            json_data = json.loads(match.group(1))
            
            # Map JSON fields to outputs
            for key in website_keys:
                if key in json_data:
                    matching_output = next((output for output in file_outputs if output.name == key), None)
                    if matching_output:
                        setattr(matching_output, 'content', json_data[key])
                        logger.debug(f"Found {key} in OpenRouter JSON block")
        
        except Exception as e:
            logger.warning(f"Error processing OpenRouter format: {str(e)}")
    
    def _extract_output_content(self, 
                               output: PatternOutput, 
                               response: Union[str, Dict], 
                               json_data: Dict) -> Optional[str]:
        """
        Extract content for a pattern output using various strategies.
        
        Args:
            output: The pattern output
            response: The AI response
            json_data: Extracted JSON data
            
        Returns:
            Optional[str]: Extracted content or None if not found
        """
        output_name = output.name
        output_type = output.output_type.value
        
        # First check if content is already set from result field
        if hasattr(output, 'content'):
            return getattr(output, 'content')
        
        # APPROACH 1: Try direct JSON access by name
        if output_name in json_data:
            return json_data[output_name]
        
        # APPROACH 1.1: Check if in nested result field
        if 'result' in json_data and isinstance(json_data['result'], dict):
            result_data = json_data['result']
            if output_name in result_data:
                return result_data[output_name]
        
        # APPROACH 2: Try common field names based on type
        if output_type == "html" and "html_content" in json_data:
            return json_data["html_content"]
        elif output_type == "css" and "css_styles" in json_data:
            return json_data["css_styles"]
        elif output_type == "js" and ("javascript_code" in json_data or "script" in json_data):
            return json_data.get("javascript_code") or json_data.get("script")
        
        # APPROACH 3: Extract from markdown code blocks
        content = self._extract_from_code_blocks(response, output_type)
        if content:
            return content
            
        # APPROACH 4: Check for direct content by pattern
        if output_type == "html":
            html_match = re.search(r'<!DOCTYPE html[^>]*>[\s\S]*?</html>', str(response))
            if html_match:
                content = html_match.group(0)
                # Clean up escaped characters
                return self._clean_escaped_content(content)
                
        # CSS and JS detection handled similarly
        
        return None
    
    def _extract_from_code_blocks(self, response: Union[str, Dict], output_type: str) -> Optional[str]:
        """
        Extract content from markdown code blocks.
        
        Args:
            response: The AI response
            output_type: Type of content to extract (html, css, js, etc.)
            
        Returns:
            Optional[str]: Extracted content or None
        """
        # Handle dictionary with nested content in OpenRouter format
        if isinstance(response, dict) and 'choices' in response:
            for choice in response['choices']:
                if isinstance(choice, dict) and 'message' in choice:
                    message = choice['message']
                    if isinstance(message, dict) and 'content' in message:
                        message_content = message['content']
                        if isinstance(message_content, str):
                            # Look for code blocks
                            pattern = rf'```{output_type}([\s\S]*?)```'
                            matches = re.finditer(pattern, message_content, re.IGNORECASE)
                            
                            for match in matches:
                                content = match.group(1).strip()
                                return self._clean_escaped_content(content)
                                
                            # Look for section headers
                            header_pattern = rf'##\s*{output_type}\s+Content.*?\n([\s\S]*?)(?=##|\Z)'
                            header_matches = re.finditer(header_pattern, message_content, re.IGNORECASE)
                            
                            for match in header_matches:
                                section_content = match.group(1).strip()
                                # Extract code block from section
                                block_match = re.search(rf'```(?:{output_type})?([\s\S]*?)```', section_content)
                                if block_match:
                                    content = block_match.group(1).strip()
                                    return self._clean_escaped_content(content)
        
        # Handle direct string response
        if isinstance(response, str):
            # Look for code blocks
            pattern = rf'```{output_type}([\s\S]*?)```'
            matches = re.finditer(pattern, response, re.IGNORECASE)
            
            for match in matches:
                content = match.group(1).strip()
                return self._clean_escaped_content(content)
            
            # Look for section headers
            header_pattern = rf'#{{"1,6"}}\s*{output_type}\s+Content.*?\n([\s\S]*?)(?=#{{"1,6"}}|\Z)'
            header_matches = re.finditer(header_pattern, response, re.IGNORECASE)
            
            for match in header_matches:
                section_content = match.group(1).strip()
                # Extract code block from section
                block_match = re.search(rf'```(?:{output_type})?([\s\S]*?)```', section_content)
                if block_match:
                    content = block_match.group(1).strip()
                    return self._clean_escaped_content(content)
        
        return None
    
    def _clean_escaped_content(self, content: str) -> str:
        """
        Clean up escaped characters in content.
        
        Args:
            content: The content to clean
            
        Returns:
            str: The cleaned content
        """
        # Remove escape sequences
        return content.replace('\\n', '\n').replace('\\"', '"').\
                     replace('\\\\', '\\').replace('\\\n', '\n').\
                     replace('\\', '')
    
    def _write_pattern_output(self, output: PatternOutput, content: Any, output_dir: str) -> Optional[str]:
        """
        Write pattern output content to a file.
        
        Args:
            output: The pattern output
            content: The content to write
            output_dir: Directory to write to
            
        Returns:
            Optional[str]: The file path if successful, None otherwise
        """
        filename = output.write_to_file
        output_type = output.output_type.value
        
        # Convert to string if needed
        if not isinstance(content, str):
            if isinstance(content, (dict, list)):
                content = json.dumps(content, indent=2)
            else:
                content = str(content)
        
        # Determine the file path
        file_path = self._determine_file_path(output_type, filename, output_dir)
        if not file_path:
            return None
        
        # Create necessary directories
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        
        # Write content to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Saved {output_type} content to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error writing file: {str(e)}")
            return None
    
    def _determine_file_path(self, output_type: str, filename: str, output_dir: str) -> str:
        """
        Determine the appropriate file path based on output type.
        
        Args:
            output_type: Type of output (html, css, js)
            filename: Specified filename
            output_dir: Base output directory
            
        Returns:
            str: The determined file path
        """
        # Handle special cases for web files
        if output_type == "html":
            return os.path.join(output_dir, "index.html")
        elif output_type == "css":
            css_dir = os.path.join(output_dir, "css")
            os.makedirs(css_dir, exist_ok=True)
            return os.path.join(css_dir, "styles.css")
        elif output_type == "js":
            js_dir = os.path.join(output_dir, "js")
            os.makedirs(js_dir, exist_ok=True)
            return os.path.join(js_dir, "script.js")
        
        # Default case: use the provided filename
        return os.path.join(output_dir, filename)
    
    def _get_output_directory(self, interactive: bool = True) -> Optional[str]:
        """
        Get the directory where files should be written, with optional user interaction.
        
        Args:
            interactive (bool): Whether to prompt the user interactively
            
        Returns:
            Optional[str]: Directory path, or None if user cancelled
        """
        # If we already have a configured output directory, use it
        if self.output_dir:
            logger.debug(f"Using configured output directory: {self.output_dir}")
            return self.output_dir
            
        # Non-interactive mode - use current directory
        if not interactive:
            logger.debug("Using current directory for file output")
            return str(Path(".").resolve())
        
        print("\n📁 File Output Location")
        print("=" * 50)
        print("The system will create files automatically.")
        print("Hint: Use '.' for current directory or specify a path like './my-website'")
        
        try:
            directory = input("Enter directory path (or 'cancel' to skip file creation): ").strip()
        except (KeyboardInterrupt, EOFError) as e:
            logger.warning(f"Input error: {str(e)}")
            return None
        
        if directory.lower() == 'cancel':
            return None
        
        # Default to current directory if empty
        if not directory:
            directory = "."
        
        # Expand relative paths
        directory = os.path.expanduser(directory)
        directory_path = Path(directory)
        
        # Check if directory exists
        if directory_path.exists():
            if directory_path.is_dir():
                return str(directory_path.resolve())
            else:
                print(f"❌ '{directory}' exists but is not a directory. Using current directory instead.")
                return str(Path(".").resolve())
        else:
            # Directory doesn't exist, ask to create
            print(f"📂 Directory '{directory}' does not exist.")
            try:
                create = input("Create this directory? (y/n): ").strip().lower()
                if create in ['y', 'yes', '']:
                    os.makedirs(directory_path, exist_ok=True)
                    return str(directory_path.resolve())
                else:
                    print("Using current directory instead.")
                    return str(Path(".").resolve())
            except (KeyboardInterrupt, EOFError):
                print("Cancelled. Using current directory instead.")
                return str(Path(".").resolve())
