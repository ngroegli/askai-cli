import os
import json
import re
import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
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

    def process_output(self, output, 
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
            system_outputs (List[SystemOutput], optional): System-defined outputs
            
        Returns:
            Tuple[str, List[str]]: The formatted output and list of created files
        """
        # Save original output in case we need the dictionary structure
        original_output = output
        output_str = output
        
        # Convert dict response to string if needed, but preserve original dict
        if isinstance(output, dict):
            # Try to extract the text content from common API response formats
            if 'content' in output:
                output_str = output['content']
            elif 'text' in output:
                output_str = output['text']
            elif 'message' in output:
                output_str = output['message']
            elif 'choices' in output and output['choices'] and isinstance(output['choices'], list):
                for choice in output['choices']:
                    if isinstance(choice, dict):
                        if 'message' in choice and 'content' in choice['message']:
                            output_str = choice['message']['content']
                            break
                        elif 'text' in choice:
                            output_str = choice['text']
                            break
            else:
                # As a last resort, convert the entire dictionary to JSON string
                import json
                try:
                    output_str = json.dumps(output, indent=2)
                except:
                    output_str = str(output)
        elif not isinstance(output, str):
            # Handle other non-string types
            output_str = str(output)
            
        # Handle pattern-defined outputs first if provided
        if pattern_outputs and file_output:
            created_files = self._handle_pattern_outputs(output, pattern_outputs)
            if created_files:
                # Format output for console
                formatted_output = output
                if console_output:
                    formatted_output = self.console_formatter.format(output)
                
                return formatted_output, created_files
        # Default to empty dict if None
        output_config = output_config or {}
        created_files = []
        
        # Store the format type if it's in the output_config
        # This would typically come from the command line -f/--format parameter
        output_format = output_config.get('format', 'rawtext')
        
        # Extract HTML content
        html_content = self.html_extractor.extract(output_str)
        if html_content and file_output:
            html_filename = output_config.get('html_filename', 'output.html')
            if self.output_dir:
                os.makedirs(self.output_dir, exist_ok=True)
                html_path = os.path.join(self.output_dir, html_filename)
                with open(html_path, 'w') as f:
                    f.write(html_content)
                created_files.append(html_path)
                logger.info(f"HTML content saved to {html_path}")
            
        # Extract CSS content
        css_content = self.css_extractor.extract(output)
        if css_content and file_output:
            css_filename = output_config.get('css_filename', 'styles.css')
            if self.output_dir:
                os.makedirs(self.output_dir, exist_ok=True)
                css_path = os.path.join(self.output_dir, css_filename)
                with open(css_path, 'w') as f:
                    f.write(css_content)
                created_files.append(css_path)
                logger.info(f"CSS content saved to {css_path}")
            
        # Extract JavaScript content
        js_content = self.js_extractor.extract(output)
        if js_content and file_output:
            js_filename = output_config.get('js_filename', 'script.js')
            if self.output_dir:
                os.makedirs(self.output_dir, exist_ok=True)
                js_path = os.path.join(self.output_dir, js_filename)
                with open(js_path, 'w') as f:
                    f.write(js_content)
                created_files.append(js_path)
                logger.info(f"JavaScript content saved to {js_path}")
            
        # Extract JSON content
        json_content = self.json_extractor.extract(output)
        if json_content and file_output:
            json_filename = output_config.get('json_filename', 'data.json')
            if self.output_dir:
                os.makedirs(self.output_dir, exist_ok=True)
                json_path = os.path.join(self.output_dir, json_filename)
                
                # Ensure we have a string for writing
                import json as json_module  # Local import to avoid scope issues
                if isinstance(json_content, dict):
                    json_str = json_module.dumps(json_content, indent=2)
                else:
                    json_str = str(json_content)
                    
                with open(json_path, 'w') as f:
                    f.write(json_str)
                created_files.append(json_path)
                logger.info(f"JSON content saved to {json_path}")
        
        # Extract Markdown content
        markdown_content = self.markdown_extractor.extract(output_str)
        
        # Format output based on requested format
        formatted_output = output_str
        
        if console_output:
            # Check if format is specified in output_config
            if output_format == 'md':
                # Use the markdown formatter for MD format
                formatted_output = self.markdown_formatter.format(output_str, content_type='markdown')
            else:
                # Default to console formatter for other formats
                formatted_output = self.console_formatter.format(output_str)
        
        # Save markdown output to file if requested
        if markdown_content and file_output:
            markdown_filename = output_config.get('markdown_filename', 'output.md')
            if self.output_dir:
                markdown_path = self.markdown_writer.write(
                    markdown_content, 
                    filename=markdown_filename
                )
                created_files.append(markdown_path)
                logger.info(f"Markdown content saved to {markdown_path}")
        
        return formatted_output, created_files
        
    def _handle_pattern_outputs(self, response, pattern_outputs):
        """Handle pattern-defined outputs as specified in the pattern markdown file.
        
        Args:
            response: The AI response (either text or dictionary)
            pattern_outputs: List of PatternOutput objects to process
            
        Returns:
            list: A list of created files
        """
        import re
        import json as json_module  # Use a different name to avoid potential conflicts
        
        created_files = []
        
        if not pattern_outputs:
            print("No outputs defined in pattern")
            return created_files
        
        # Filter outputs that should be written to files
        file_outputs = [
            output for output in pattern_outputs
            if output.should_write_to_file()
        ]
        
        if not file_outputs:
            print("No file outputs specified")
            return created_files
        
        # Get the output directory, prompting the user if needed
        output_dir = self._get_output_directory(interactive=True)
        if not output_dir:
            print("User cancelled output directory selection")
            return created_files
            
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"🔍 Processing response for {len(file_outputs)} file outputs...")
        # Detect if response is dictionary or string
        if isinstance(response, dict):
            print("🔍 Response is a dictionary")
            
            # Check for OpenRouter API response format
            if 'choices' in response and isinstance(response['choices'], list) and response['choices']:
                first_choice = response['choices'][0]
                if isinstance(first_choice, dict) and 'message' in first_choice:
                    message = first_choice['message']
                    if isinstance(message, dict) and 'content' in message:
                        # Extract content from OpenRouter response
                        message_content = message['content']
                        print("✅ Found OpenRouter API response format")
                        
                        # Try to extract JSON from the content field
                        if isinstance(message_content, str) and '{' in message_content and '}' in message_content:
                            try:
                                # Look for JSON object in the message content
                                match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', message_content)
                                if match:
                                    json_text = match.group(1)
                                    json_data = json_module.loads(json_text)
                                    print("✅ Found JSON in markdown code block inside OpenRouter response")
                                else:
                                    # No need to parse the whole response as it's not likely to be valid JSON
                                    json_data = {}
                            except json_module.JSONDecodeError:
                                print("⚠️ Could not parse JSON from OpenRouter content, treating as text")
                                json_data = {}
                        else:
                            json_data = {}
                    else:
                        json_data = response
                else:
                    json_data = response
            else:
                json_data = response
        else:
            print("🔍 Response is a string, trying to extract JSON")
            # Try to extract JSON
            try:
                # Look for JSON object in the response
                match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', str(response))
                if match:
                    json_text = match.group(1)
                    json_data = json_module.loads(json_text)
                    print("✅ Found JSON in markdown code block")
                else:
                    # Try parsing the whole response as JSON
                    json_data = json_module.loads(str(response))
                    print("✅ Parsed entire response as JSON")
            except json_module.JSONDecodeError:
                print("⚠️ Could not parse JSON, treating as text")
                json_data = {}
        
        import re
        
        # DIRECT FILE WRITING FROM JSON OR TEXT
        for output in file_outputs:
            filename = output.write_to_file
            output_name = output.name
            output_type = output.output_type.value
            
            print(f"\n🔍 Processing output: name={output_name}, type={output_type}, file={filename}")
            
            content = None
            
            # Check if the response is nested within a 'content' field
            if 'content' in response:
                try:
                    # Try to extract JSON from the content field
                    content_str = response['content']
                    # Check if it's a JSON string
                    if isinstance(content_str, str) and '{' in content_str and '}' in content_str:
                        try:
                            # Try to parse it as JSON
                            match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', content_str)
                            if match:
                                extracted_json = json_module.loads(match.group(1))
                                json_data = extracted_json
                                print("✅ Found JSON in content field")
                        except json_module.JSONDecodeError:
                            pass
                except Exception as e:
                    print(f"⚠️ Error extracting from content: {str(e)}")

            # APPROACH 1: Try to get directly from JSON by name
            if json_data and output_name in json_data:
                print(f"✅ Found {output_name} in JSON data")
                content = json_data[output_name]
                
            # APPROACH 2: Try common field names based on type
            elif json_data:
                if output_type == "html" and "html_content" in json_data:
                    print("✅ Found html_content in JSON data")
                    content = json_data["html_content"]
                elif output_type == "css" and "css_styles" in json_data:
                    print("✅ Found css_styles in JSON data")
                    content = json_data["css_styles"]
                elif output_type == "js" and ("javascript_code" in json_data or "script" in json_data):
                    print("✅ Found javascript_code/script in JSON data")
                    content = json_data.get("javascript_code") or json_data.get("script")
            
            # APPROACH 3: Extract from text using regex patterns
            if content is None:
                print("🔍 Trying to extract content from text...")
                
                # If the response is a dictionary with message content
                if isinstance(response, dict) and 'choices' in response:
                    for choice in response['choices']:
                        if isinstance(choice, dict) and 'message' in choice:
                            message = choice['message']
                            if isinstance(message, dict) and 'content' in message:
                                message_content = message['content']
                                if isinstance(message_content, str):
                                    # Look for markdown code blocks with the right type
                                    pattern = rf'```{output_type}([\s\S]*?)```'
                                    matches = re.finditer(pattern, message_content, re.IGNORECASE)
                                    
                                    for match in matches:
                                        content = match.group(1).strip()
                                        # Clean up escape characters
                                        content = content.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                                        content = content.replace('\\\n', '\n').replace('\\', '')
                                        print(f"✅ Found content in {output_type} code block ({len(content)} chars)")
                                        break
                                    
                                    # If still not found, look for section headers
                                    if content is None:
                                        header_pattern = rf'##\s*{output_type}\s+Content.*?\n([\s\S]*?)(?=##|\Z)'
                                        header_matches = re.finditer(header_pattern, message_content, re.IGNORECASE)
                                        
                                        for match in header_matches:
                                            section_content = match.group(1).strip()
                                            # Extract code block from section
                                            block_match = re.search(rf'```(?:{output_type})?([\s\S]*?)```', section_content)
                                            if block_match:
                                                content = block_match.group(1).strip()
                                                # Clean up escape characters
                                                content = content.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                                                content = content.replace('\\\n', '\n').replace('\\', '')
                                                print(f"✅ Found content in section header and code block ({len(content)} chars)")
                                                break
                
                # Try with direct response string
                elif isinstance(response, str):
                    # Look for markdown code blocks with the right type
                    pattern = rf'```{output_type}([\s\S]*?)```'
                    matches = re.finditer(pattern, response, re.IGNORECASE)
                    
                    for match in matches:
                        content = match.group(1).strip()
                        print(f"✅ Found content in {output_type} code block ({len(content)} chars)")
                        break
                    
                    # If still not found, look for section headers
                    if content is None:
                        header_pattern = rf'#{{"1,6"}}\s*{output_type}\s+Content.*?\n([\s\S]*?)(?=#{{"1,6"}}|\Z)'
                        header_matches = re.finditer(header_pattern, response, re.IGNORECASE)
                        
                        for match in header_matches:
                            section_content = match.group(1).strip()
                            # Extract code block from section
                            block_match = re.search(rf'```(?:{output_type})?([\s\S]*?)```', section_content)
                            if block_match:
                                content = block_match.group(1).strip()
                                print(f"✅ Found content in section header and code block ({len(content)} chars)")
                                break
            
            # APPROACH 3: Extract from text using regex patterns
            if content is None and isinstance(response, str):
                print(f"🔍 Trying to extract {output_type} content from response text...")
                # Look for markdown code blocks with the right type
                pattern = rf'```{output_type}([\s\S]*?)```'
                matches = re.finditer(pattern, response, re.IGNORECASE)
                
                for match in matches:
                    content = match.group(1).strip()
                    print(f"✅ Found content in {output_type} code block ({len(content)} chars)")
                    break
                
                # If still not found, look for section headers
                if content is None:
                    header_pattern = rf'#{{"1,6"}}\s*{output_type}\s+Content.*?\n([\s\S]*?)(?=#{{"1,6"}}|\Z)'
                    header_matches = re.finditer(header_pattern, response, re.IGNORECASE)
                    
                    for match in header_matches:
                        section_content = match.group(1).strip()
                        # Extract code block from section
                        block_match = re.search(rf'```(?:{output_type})?([\s\S]*?)```', section_content)
                        if block_match:
                            content = block_match.group(1).strip()
                            print(f"✅ Found content in section header and code block ({len(content)} chars)")
                            break

            # Final attempt - try to find any HTML, CSS, or JS directly in the response
            if content is None:
                response_text = str(response)
                
                # Direct HTML detection
                if output_type == "html":
                    html_match = re.search(r'<!DOCTYPE html[^>]*>[\s\S]*?</html>', response_text)
                    if html_match:
                        content = html_match.group(0)
                        # Remove any backslashes that might be escapes
                        content = content.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                        # Remove any remaining backslashes
                        content = content.replace('\\\n', '\n').replace('\\', '')
                        print(f"✅ Found direct HTML content in response ({len(content)} chars)")
                
                # Direct CSS detection
                elif output_type == "css":
                    # First try to find "css_styles": in the response
                    css_json_match = re.search(r'"css_styles"\s*:\s*"([\s\S]*?)(?:"|$)', response_text)
                    if css_json_match:
                        # Found CSS in JSON format
                        content = css_json_match.group(1)
                        # Properly unescape the content (handle \\n etc.)
                        content = content.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                        # Remove any remaining backslashes that might be at line ends
                        content = content.replace('\\\n', '\n').replace('\\', '')
                        print(f"✅ Found CSS content in JSON response ({len(content)} chars)")
                    else:
                        # Try regular pattern matching
                        css_patterns = [
                            r'/\* Base Styles \*/[\s\S]*?body\s*\{[\s\S]*?\}[\s\S]*?\.hero\s*\{',
                            r'\*\s*\{[\s\S]*?margin:\s*0;[\s\S]*?padding:\s*0;[\s\S]*?\}',
                            r'body\s*\{[\s\S]*?font-family[\s\S]*?\}[\s\S]*?h1,\s*h2'
                        ]
                        
                        for pattern in css_patterns:
                            css_match = re.search(pattern, response_text)
                            if css_match:
                                start_pos = css_match.start()
                                end_pos = response_text[start_pos:].find('\n}') + start_pos
                                if end_pos > start_pos:
                                    content = response_text[start_pos:end_pos+2] 
                                    print(f"✅ Found direct CSS content in response ({len(content)} chars)")
                                    break
                
                # Direct JS detection
                elif output_type == "js":
                    # First try to find "javascript_code": in the response
                    js_json_match = re.search(r'"javascript_code"\s*:\s*"([\s\S]*?)(?:"|$)', response_text)
                    if js_json_match:
                        # Found JS in JSON format
                        content = js_json_match.group(1)
                        # Properly unescape the content
                        content = content.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                        # Remove any remaining backslashes that might be at line ends
                        content = content.replace('\\\n', '\n').replace('\\', '')
                        print(f"✅ Found JavaScript content in JSON response ({len(content)} chars)")
                    else:
                        # Try regular pattern matching
                        js_patterns = [
                            r'document\.addEventListener\([\'"]DOMContentLoaded[\'"],[^{]*\{[\s\S]*?\}\);',
                            r'// JavaScript for[\s\S]*?function[\s\S]*?\}',
                            r'const[\s\S]*?=[\s\S]*?\{[\s\S]*?\};'
                        ]
                        
                        for pattern in js_patterns:
                            js_match = re.search(pattern, response_text)
                            if js_match:
                                content = js_match.group(0)
                                print(f"✅ Found direct JS content in response ({len(content)} chars)")
                                break

            # Write the file if we have content
            if content is not None:
                # Convert to string if needed
                if not isinstance(content, str):
                    if isinstance(content, (dict, list)):
                        content = json_module.dumps(content, indent=2)
                    else:
                        content = str(content)
                
                # Create directory if it doesn't exist
                try:
                    os.makedirs(output_dir, exist_ok=True)
                except Exception as e:
                    print(f"⚠️ Error creating directory: {str(e)}")
                
                # Special handling for index.html file
                if output_type == "html":
                    file_path = os.path.join(output_dir, "index.html")
                    
                    # Check if we need to create css and js directories based on HTML content
                    # Look for any pattern that indicates CSS in a subdirectory
                    if re.search(r'href=[\"\']css/[^\"\']*\.css[\"\']', content) or "css/styles.css" in content:
                        css_dir = os.path.join(output_dir, "css")
                        os.makedirs(css_dir, exist_ok=True)
                        print(f"✅ Created CSS directory: {css_dir}")
                    
                    # Look for any pattern that indicates JS in a subdirectory
                    if re.search(r'src=[\"\']js/[^\"\']*\.js[\"\']', content) or "js/script.js" in content:
                        js_dir = os.path.join(output_dir, "js")
                        os.makedirs(js_dir, exist_ok=True)
                        print(f"✅ Created JS directory: {js_dir}")
                        
                    # Fix any escaped HTML
                    content = content.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\').replace('\\\n', '\n').replace('\\', '')
                elif output_type == "css":
                    # Check if this is part of a website with HTML and reference to css/styles.css
                    if content and "css/styles.css" in str(content) or \
                       any(output.output_type == OutputType.HTML and output.content and "css/styles.css" in str(output.content) for output in file_outputs if hasattr(output, 'content')) or \
                       os.path.exists(os.path.join(output_dir, "css")):
                        # Use the css subdirectory
                        css_dir = os.path.join(output_dir, "css")
                        os.makedirs(css_dir, exist_ok=True)
                        file_path = os.path.join(css_dir, "styles.css")
                        print(f"Using CSS path from HTML reference: {file_path}")
                    else:
                        file_path = os.path.join(output_dir, "style.css")
                elif output_type == "js":
                    # Check if this is part of a website with HTML and reference to js/script.js
                    if content and "js/script.js" in str(content) or \
                       any(output.output_type == OutputType.HTML and output.content and "js/script.js" in str(output.content) for output in file_outputs if hasattr(output, 'content')) or \
                       os.path.exists(os.path.join(output_dir, "js")):
                        # Use the js subdirectory
                        js_dir = os.path.join(output_dir, "js")
                        os.makedirs(js_dir, exist_ok=True)
                        file_path = os.path.join(js_dir, "script.js")
                        print(f"Using JS path from HTML reference: {file_path}")
                    else:
                        file_path = os.path.join(output_dir, "script.js")
                else:
                    file_path = os.path.join(output_dir, filename)
                
                print(f"🔍 Writing to file: {file_path}")
                
                try:
                    # Direct simple file write
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        print(f"✅ Successfully created file: {file_path} ({file_size} bytes)")
                        created_files.append(file_path)
                    else:
                        print_error_or_warnings(f"Failed to create file: {file_path}")
                except Exception as e:
                    print_error_or_warnings(f"Error writing file: {str(e)}")
                    try:
                        # Try alternative temp location
                        alt_path = f"/tmp/{filename}"
                        with open(alt_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"✅ Created file in alternative location: {alt_path}")
                        created_files.append(alt_path)
                    except Exception as e2:
                        print(f"❌ Failed alternative write: {str(e2)}")
            else:
                print(f"⚠️ No content found for {output_name}")
        
        # Return the list of created files
        return created_files
    
    def _get_output_directory(self, interactive: bool = True) -> Optional[str]:
        """Get the directory where files should be written, with optional user interaction.
        
        Args:
            interactive (bool): Whether to prompt the user interactively
            
        Returns:
            str: Directory path, or None if user cancelled
        """
        # If we already have a configured output directory, use it
        if self.output_dir:
            print(f"\n📁 Using configured output directory: {self.output_dir}")
            return self.output_dir
            
        # Non-interactive mode - use current directory
        if not interactive:
            print("\n📁 Using current directory for file output")
            directory_path = Path(".")
            return str(directory_path.resolve())
        
        print("\n📁 File Output Location")
        print("=" * 50)
        print("The system will create files automatically.")
        print("Hint: Use '.' for current directory or specify a path like './my-website'")
        print("Press Enter for current directory (.) or specify a path:")
        
        try:
            directory = input("Enter directory path (or 'cancel' to skip file creation): ").strip()
        except (KeyboardInterrupt, EOFError) as e:
            print_error_or_warnings(f"Input error: {str(e)}")
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
            except (KeyboardInterrupt, EOFError):
                return str(Path(".").resolve())
            
            if create in ['y', 'yes', '']:  # Default to yes if empty
                try:
                    directory_path.mkdir(parents=True, exist_ok=True)
                    print(f"✅ Created directory: {directory_path.resolve()}")
                    return str(directory_path.resolve())
                except Exception as e:
                    print(f"❌ Error creating directory: {str(e)}")
                    print("Using current directory instead.")
                    return str(Path(".").resolve())
            else:
                print("Using current directory instead.")
                return str(Path(".").resolve())
    
    def _extract_output_content(self, response, output: PatternOutput) -> Optional[str]:
        """Extract content for a specific output from the AI response.
        
        Args:
            response: The AI response text
            output: PatternOutput configuration
        
        Returns:
            str: Extracted content, or None if not found
        """
        output_name = output.name
        output_type = output.output_type.value
        
        # Try to extract content from markdown code blocks
        if isinstance(response, str):
            import re
            
            # First try to find a section with the output name
            # This pattern looks for markdown headers with the output name
            section_pattern = rf"(?:^|\n)#+\s*{re.escape(output_name)}.*?(?:\n```{re.escape(output_type)}([\s\S]*?)```|\n#+\s*)"
            section_match = re.search(section_pattern, response, re.IGNORECASE)
            
            # Also look for a more generic pattern like "## HTML Content" for HTML outputs
            type_section_pattern = rf"(?:^|\n)#+\s*{re.escape(output_type)}.*?Content.*?(?:\n```{re.escape(output_type)}([\s\S]*?)```|\n#+\s*)"
            type_match = re.search(type_section_pattern, response, re.IGNORECASE)
            
            # Look for code blocks of the correct type without headers
            code_block_pattern = rf"```{re.escape(output_type)}([\s\S]*?)```"
            code_match = re.search(code_block_pattern, response, re.IGNORECASE)
            
            if section_match and section_match.group(1):
                content = section_match.group(1).strip()
                print(f"✅ Found content in section '{output_name}': {len(content)} chars")
                return content
            elif type_match and type_match.group(1):
                content = type_match.group(1).strip()
                print(f"✅ Found content in type section '{output_type} Content': {len(content)} chars")
                return content
            elif code_match:
                content = code_match.group(1).strip()
                print(f"✅ Found content in code block for '{output_type}': {len(content)} chars")
                return content
        
        # Map output types to extractors
        if output_type == 'html':
            content = self.html_extractor.extract(response, output_name)
        elif output_type == 'css':
            content = self.css_extractor.extract(response, output_name)
        elif output_type == 'js':
            content = self.js_extractor.extract(response, output_name)
        elif output_type == 'json':
            content = self.json_extractor.extract(response, output_name)
        elif output_type == 'markdown':
            content = self.markdown_extractor.extract(response, output_name)
        else:
            # For other types, try to use markdown extractor
            content = self.markdown_extractor.extract(response, output_name)
        
        if content:
            print(f"✅ Found content for {output_name}: {len(content)} chars")
            return content
        else:
            print(f"❌ Could not extract content for {output_name}")
            return None
            
    def _validate_html_references(self, html_content: str, file_outputs: List[PatternOutput]) -> str:
        """Validate and fix HTML file references to match output filenames.
        
        Args:
            html_content: The HTML content to validate
            file_outputs: List of file outputs to check against
            
        Returns:
            str: Validated HTML content with correct file references
        """
        import re
        
        # Get CSS and JS filenames from outputs
        css_filename = None
        js_filename = None
        
        for output in file_outputs:
            if output.output_type == OutputType.CSS:
                css_filename = output.write_to_file
            elif output.output_type == OutputType.JS:
                js_filename = output.write_to_file
        
        # Make sure HTML has proper structure
        if not re.search(r'<html[^>]*>', html_content, re.IGNORECASE):
            html_content = f'<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Generated Page</title>\n</head>\n<body>\n{html_content}\n</body>\n</html>'
            print("🔧 Added HTML structure to content")

        # Ensure there's a head section
        if not re.search(r'<head[^>]*>', html_content, re.IGNORECASE):
            # Add a head section before the body
            body_start = html_content.find('<body')
            if body_start != -1:
                html_content = html_content[:body_start] + '<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Generated Page</title>\n</head>\n' + html_content[body_start:]
                print("🔧 Added missing head section")
        
        # Fix CSS reference if found
        if css_filename:
            # First look for any existing stylesheet link
            has_css_link = bool(re.search(r'<link[^>]*rel=["\']stylesheet["\'][^>]*>', html_content, re.IGNORECASE))
            
            if has_css_link:
                # Replace any CSS reference with the correct filename
                html_content = re.sub(
                    r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\'][^"\']*["\'][^>]*>',
                    f'<link rel="stylesheet" href="{css_filename}">',
                    html_content,
                    flags=re.IGNORECASE
                )
                print(f"🔧 Updated CSS reference to: {css_filename}")
            else:
                # No CSS link found, add it to head
                head_end = html_content.find('</head>')
                if head_end != -1:
                    css_link = f'    <link rel="stylesheet" href="{css_filename}">\n'
                    html_content = html_content[:head_end] + css_link + html_content[head_end:]
                    print(f"🔧 Added CSS reference: {css_filename}")
                else:
                    # If no head end tag found, try to add before body
                    body_start = html_content.find('<body')
                    if body_start != -1:
                        html_content = html_content[:body_start] + f'<head>\n    <link rel="stylesheet" href="{css_filename}">\n</head>\n' + html_content[body_start:]
                        print(f"🔧 Added head with CSS reference: {css_filename}")
                    else:
                        # Last resort: prepend to the content
                        html_content = f'<!DOCTYPE html>\n<html>\n<head>\n    <link rel="stylesheet" href="{css_filename}">\n</head>\n<body>\n{html_content}\n</body>\n</html>'
                        print(f"🔧 Restructured HTML and added CSS reference: {css_filename}")
        
        # Fix JS reference if found
        if js_filename:
            # Check for existing script tag with src
            has_script_tag = bool(re.search(r'<script[^>]*src=["\'][^"\']*["\'][^>]*>', html_content, re.IGNORECASE))
            
            if has_script_tag:
                # Replace any script reference with the correct filename
                html_content = re.sub(
                    r'<script[^>]*src=["\'][^"\']*["\'][^>]*></script>',
                    f'<script src="{js_filename}" defer></script>',
                    html_content,
                    flags=re.IGNORECASE
                )
                print(f"🔧 Updated JS reference to: {js_filename}")
            else:
                # Try to add before closing head tag
                head_end = html_content.find('</head>')
                if head_end != -1:
                    script_tag = f'    <script src="{js_filename}" defer></script>\n'
                    html_content = html_content[:head_end] + script_tag + html_content[head_end:]
                    print(f"🔧 Added JS reference: {js_filename}")
                else:
                    # If no head end tag, try to add before body
                    body_start = html_content.find('<body')
                    if body_start != -1:
                        html_content = html_content[:body_start] + f'<script src="{js_filename}" defer></script>\n' + html_content[body_start:]
                        print(f"🔧 Added JS reference: {js_filename}")
                    else:
                        # Last resort: add at the end of the content
                        html_content = html_content + f'\n<script src="{js_filename}" defer></script>\n'
                        print(f"🔧 Added JS reference at end: {js_filename}")
        
        return html_content
