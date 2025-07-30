"""
Output processing and handling module.
Manages different output formats and file writing.
"""

import json
import re
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.markdown import Markdown
from systems.system_outputs import SystemOutput, OutputType


class OutputHandler:
    """Handles different types of output processing."""
    
    def __init__(self, logger):
        self.logger = logger

    def write_to_file(self, path, content):
        """Write content to a file."""
        with open(path, "w") as f:
            f.write(content)

    def render_markdown(self, markdown_content):
        """Print markdown text as rendered markdown to the console."""
        console = Console()
        md = Markdown(markdown_content)
        console.print(md)

    def handle_output(self, response, args, system_outputs=None):
        """Handle the output of the AI response based on arguments.
        
        Args:
            response: The AI response (can be string or dict with content/annotations)
            args: Command line arguments
            system_outputs: Optional list of SystemOutput objects for auto-execution
        
        Returns:
            bool: True if output was handled and program should exit, False otherwise
        """
        # Handle new response format with web search annotations
        content = response
        annotations = []
        
        if isinstance(response, dict):
            content = response.get("content", str(response))
            annotations = response.get("annotations", [])
        
        # Display web search sources if present
        if annotations:
            self._display_web_sources(annotations)
        
        # First, handle normal output display
        should_exit = False
        
        if args.output:
            self.logger.info(json.dumps({
                "log_message": "Writing response to output file", 
                "output_file": args.output
            }))
            self.write_to_file(args.output, content)
            print(f"Response written to {args.output}")
            should_exit = True
        elif args.format == "md" and not args.plain_md:
            self.logger.info(json.dumps({"log_message": "Rendering response as markdown"}))
            self.render_markdown(content)
        else:
            self.logger.info(json.dumps({"log_message": "Printing response as raw text"}))
            print(content)
        
        # Handle file writing based on system outputs
        if system_outputs:
            self._handle_file_outputs(content, system_outputs)
        
        # After displaying output, handle auto-execution of code outputs if system outputs are provided
        if system_outputs and not should_exit:
            self._handle_auto_execution(content, system_outputs)
        
        return should_exit

    def _display_web_sources(self, annotations):
        """Display web search sources with proper formatting.
        
        Args:
            annotations: List of annotation dictionaries from OpenRouter API
        """
        if not annotations:
            return
            
        print("\n🔍 Web Search Sources:")
        print("=" * 50)
        
        for i, annotation in enumerate(annotations, 1):
            if annotation.get("type") == "url_citation":
                citation = annotation.get("url_citation", {})
                url = citation.get("url", "Unknown URL")
                title = citation.get("title", "Unknown Title")
                content = citation.get("content", "")
                
                print(f"{i}. {title}")
                print(f"   🔗 {url}")
                
                # Show a brief content preview if available
                if content:
                    preview = content[:150].replace('\n', ' ').strip()
                    if len(content) > 150:
                        preview += "..."
                    print(f"   📄 {preview}")
                
                print()
        
        print("=" * 50)
        print()

    def _handle_file_outputs(self, response: str, system_outputs: List[SystemOutput]) -> None:
        """Handle writing outputs to files based on system output configurations.
        
        Args:
            response: The AI response text
            system_outputs: List of SystemOutput objects to check for file writing
        """
        # Find outputs that should be written to files
        file_outputs = [output for output in system_outputs if output.should_write_to_file()]
        
        if not file_outputs:
            return
        
        # Show what files will be created
        print(f"\n🎯 Found {len(file_outputs)} files to create:")
        for output in file_outputs:
            print(f"  • {output.write_to_file} ({output.output_type.value})")
        
        # Ask for base directory once for all file outputs
        base_dir = self._get_output_directory()
        if base_dir is None:
            return  # User cancelled
        
        # Process each file output
        for output in file_outputs:
            try:
                # Extract content for this output
                content = self._extract_output_content(response, output)
                if content:
                    # Validate HTML file references for web projects
                    if output.output_type == OutputType.HTML:
                        content = self._validate_html_references(content, file_outputs)
                    
                    # Create full file path
                    file_path = Path(base_dir) / output.write_to_file
                    
                    # Write the file
                    self._write_output_file(file_path, content, output)
                    print(f"✅ Created: {file_path}")
                else:
                    print(f"⚠️  No content found for {output.name}")
                    
            except Exception as e:
                print(f"❌ Error writing {output.write_to_file}: {str(e)}")
                self.logger.error(json.dumps({
                    "log_message": "File writing error",
                    "output_name": output.name,
                    "filename": output.write_to_file,
                    "error": str(e)
                }))

    def _get_output_directory(self) -> Optional[str]:
        """Get the directory where files should be written, with user interaction.
        
        Returns:
            str: Directory path, or None if user cancelled
        """
        print("\n📁 File Output Location")
        print("=" * 50)
        print("The system will create files automatically.")
        print("Hint: Use '.' for current directory or specify a path like './my-website'")
        print("Press Enter for current directory (.) or specify a path:")
        
        try:
            directory = input("Enter directory path (or 'cancel' to skip file creation): ").strip()
        except (KeyboardInterrupt, EOFError):
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

    def _extract_output_content(self, response: str, output: SystemOutput) -> Optional[str]:
        """Extract content for a specific output from the AI response.
        
        This method handles different response formats:
        1. JSON format (for programmatic parsing)
        2. Markdown format (for human-readable output)
        3. Mixed text format (fallback)
        
        Args:
            response: The AI response text
            output: SystemOutput configuration
        
        Returns:
            str: Extracted content, or None if not found
        """
        print(f"\n🔍 Extracting '{output.name}' content...")
        
        # Strategy 1: Try JSON extraction first (most reliable for file outputs)
        content = self._extract_from_json(response, output)
        if content:
            return content
        
        # Strategy 2: Try structured markdown patterns
        content = self._extract_from_markdown(response, output)
        if content:
            return content
        
        # Strategy 3: Try code block patterns
        content = self._extract_from_code_blocks(response, output)
        if content:
            return content
        
        # Strategy 4: Try simpler patterns as last resort
        content = self._extract_simple_patterns(response, output)
        if content:
            return content
        
        print(f"❌ No content found for '{output.name}'")
        return None

    def _extract_from_json(self, response: str, output: SystemOutput) -> Optional[str]:
        """Extract content from JSON format responses."""
        json_patterns = [
            r'HERE THE RESULT:\s*```json\s*\n(.*?)\n```',
            r'HERE THE RESULT:\s*\n(\{.*?\})',
            r'```json\s*\n(.*?)\n```',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    json_data = json.loads(match.strip())
                    if isinstance(json_data, dict) and output.name in json_data:
                        content = json_data[output.name]
                        if isinstance(content, str):
                            print(f"✅ Found content via JSON: {len(content)} chars")
                            return content
                except json.JSONDecodeError:
                    continue
        return None

    def _extract_from_markdown(self, response: str, output: SystemOutput) -> Optional[str]:
        """Extract content from markdown-structured responses."""
        # Look for markdown sections with the output name
        patterns = [
            # ## HTML Content or ### HTML Content
            rf'^#{2,3}\s*{re.escape(output.name)}.*?\n(.*?)(?=\n#{1,3}\s|\Z)',
            # HTML Content: or **HTML Content:**
            rf'(?:\*\*)?{re.escape(output.name)}(?:\*\*)?[:\s]*\n(.*?)(?=\n(?:\*\*)?[A-Z][a-z]+(?:\*\*)?\s*[:\s]|\Z)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            for match in matches:
                content = match.strip()
                # Remove markdown formatting and code block markers
                content = re.sub(r'^```[a-z]*\s*\n', '', content)
                content = re.sub(r'\n```\s*$', '', content)
                if len(content) > 20:
                    print(f"✅ Found content via markdown: {len(content)} chars")
                    return content
        return None

    def _extract_from_code_blocks(self, response: str, output: SystemOutput) -> Optional[str]:
        """Extract content from code blocks."""
        output_type = output.output_type.value.lower()
        
        patterns = [
            # Code block with specific language
            rf'```{output_type}\s*\n(.*?)\n```',
            # Code block with output name nearby
            rf'{re.escape(output.name)}.*?```(?:{output_type})?\s*\n(.*?)\n```',
            # Any code block if output type matches common web languages
            rf'```(?:html|css|javascript|js)?\s*\n(.*?)\n```' if output_type in ['html', 'css', 'js'] else None,
        ]
        
        # Remove None patterns
        patterns = [p for p in patterns if p is not None]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
            for match in matches:
                content = match.strip()
                if len(content) > 20 and self._is_valid_content(content, output_type):
                    print(f"✅ Found content via code block: {len(content)} chars")
                    return content
        return None

    def _is_valid_content(self, content: str, output_type: str) -> bool:
        """Validate that content matches the expected output type."""
        content_lower = content.lower()
        
        if output_type == 'html':
            return any(tag in content_lower for tag in ['<html', '<div', '<body', '<head', '<!doctype'])
        elif output_type == 'css':
            return '{' in content and '}' in content and (':' in content)
        elif output_type == 'js':
            return any(keyword in content_lower for keyword in ['function', 'var ', 'let ', 'const ', '=>'])
        
        return True  # For other types, assume valid

    def _extract_simple_patterns(self, response: str, output: SystemOutput) -> Optional[str]:
        """Extract content using simple, broad patterns as last resort."""
        output_type = output.output_type.value.lower()
        
        # Very broad patterns to catch any code blocks
        simple_patterns = [
            # Any HTML content
            r'<!DOCTYPE html.*?</html>' if output_type == 'html' else None,
            # Any CSS content (look for selectors and rules)
            r'(?:^|\n)([^{}]*\{[^{}]*\}[^{}]*(?:\{[^{}]*\}[^{}]*)*?)(?=\n\n|\n[A-Z]|\Z)' if output_type == 'css' else None,
            # Any JavaScript content
            r'(?:document\.|function|const|let|var|=>).*?(?=\n\n|\n[A-Z]|\Z)' if output_type == 'js' else None,
        ]
        
        # Remove None patterns
        simple_patterns = [p for p in simple_patterns if p is not None]
        
        for pattern in simple_patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            for match in matches:
                content = match.strip()
                if len(content) > 50:  # Ensure it's substantial
                    print(f"✅ Found content via simple pattern: {len(content)} chars")
                    return content
        
        return None

    def _validate_html_references(self, html_content: str, file_outputs: List[SystemOutput]) -> str:
        """Validate and fix HTML file references to match output filenames.
        
        Args:
            html_content: The HTML content to validate
            file_outputs: List of file outputs to check against
            
        Returns:
            str: Validated HTML content with correct file references
        """
        # Get CSS and JS filenames from outputs
        css_filename = None
        js_filename = None
        
        for output in file_outputs:
            if output.output_type == OutputType.CSS:
                css_filename = output.write_to_file
            elif output.output_type == OutputType.JS:
                js_filename = output.write_to_file
        
        # Fix CSS reference if found
        if css_filename:
            # Replace any CSS reference with the correct filename
            import re
            html_content = re.sub(
                r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\'][^"\']*["\'][^>]*>',
                f'<link rel="stylesheet" href="{css_filename}">',
                html_content,
                flags=re.IGNORECASE
            )
            
            # If no CSS link found, add it to head
            if 'rel="stylesheet"' not in html_content.lower():
                head_end = html_content.find('</head>')
                if head_end != -1:
                    css_link = f'    <link rel="stylesheet" href="{css_filename}">\n'
                    html_content = html_content[:head_end] + css_link + html_content[head_end:]
                    print(f"🔧 Added CSS reference: {css_filename}")
        
        # Fix JS reference if found
        if js_filename:
            # Replace any script reference with the correct filename
            html_content = re.sub(
                r'<script[^>]*src=["\'][^"\']*["\'][^>]*></script>',
                f'<script src="{js_filename}" defer></script>',
                html_content,
                flags=re.IGNORECASE
            )
            
            # If no script tag found, add it to head
            if f'src="{js_filename}"' not in html_content:
                head_end = html_content.find('</head>')
                if head_end != -1:
                    script_tag = f'    <script src="{js_filename}" defer></script>\n'
                    html_content = html_content[:head_end] + script_tag + html_content[head_end:]
                    print(f"🔧 Added JS reference: {js_filename}")
        
        return html_content

    def _write_output_file(self, file_path: Path, content: str, output: SystemOutput) -> None:
        """Write content to a file.
        
        Args:
            file_path: Path where to write the file
            content: Content to write
            output: SystemOutput configuration
        """
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Log the file creation
        self.logger.info(json.dumps({
            "log_message": "File written from system output",
            "output_name": output.name,
            "output_type": output.output_type.value,
            "filename": str(file_path),
            "content_length": len(content)
        }))

    def _handle_auto_execution(self, response: str, system_outputs: List[SystemOutput]) -> None:
        """Handle auto-execution of code outputs with user prompts.
        
        Args:
            response: The AI response text
            system_outputs: List of SystemOutput objects to check for auto-execution
        """
        # Find outputs that should prompt for execution
        auto_exec_outputs = [output for output in system_outputs if output.should_prompt_for_execution()]
        
        if not auto_exec_outputs:
            return
        
        # Extract code blocks from the response for each auto-execution output
        for output in auto_exec_outputs:
            code_blocks = self._extract_code_blocks(response, output.name)
            
            for i, code_block in enumerate(code_blocks):
                # Skip empty code blocks
                if not code_block.strip():
                    continue
                
                # Determine the display name for the output
                display_name = f"{output.name}" + (f" (block {i+1})" if len(code_blocks) > 1 else "")
                
                # Prompt user for execution
                if SystemOutput.prompt_for_execution(code_block, display_name):
                    self._execute_command(code_block, display_name)

    def _extract_code_blocks(self, response: str, output_name: str) -> List[str]:
        """Extract code blocks from the AI response for a specific output.
        
        Args:
            response: The AI response text
            output_name: The name of the output to extract code for
        
        Returns:
            List[str]: List of extracted code blocks
        """
        code_blocks = []
        
        # First, try to find code blocks specifically labeled with the output name
        # Look for patterns like "command:" followed by code blocks
        output_pattern = rf'{re.escape(output_name)}:\s*```(?:bash|shell|sh)?\s*\n(.*?)\n```'
        matches = re.findall(output_pattern, response, re.DOTALL | re.IGNORECASE)
        
        if matches:
            for match in matches:
                cleaned_code = match.strip()
                if cleaned_code:
                    code_blocks.append(cleaned_code)
            return code_blocks
        
        # If no labeled blocks found, look for general code blocks but be more selective
        patterns = [
            rf'```(?:bash|shell|sh)\s*\n(.*?)\n```',  # Bash/shell specific code blocks
            rf'```\s*\n([^`]*(?:pkill|kill|ps|grep|find|ls|cd|mkdir|rm|cp|mv|cat|sudo|chmod|chown|tar|zip|wget|curl|git|docker|systemctl)[^`]*)\n```',  # Code blocks with common commands
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
            for match in matches:
                cleaned_code = match.strip()
                if cleaned_code and self._looks_like_command(cleaned_code):
                    code_blocks.append(cleaned_code)
        
        # If still no code blocks found, try to find single-line commands
        if not code_blocks:
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line and self._looks_like_command(line) and not line.startswith('#'):
                    # Only include if it's a reasonably short command (likely a one-liner)
                    if len(line) < 200:
                        code_blocks.append(line)
        
        return code_blocks

    def _looks_like_command(self, text: str) -> bool:
        """Simple heuristic to determine if text looks like a shell command.
        
        Args:
            text: Text to check
            
        Returns:
            bool: True if text looks like a command
        """
        # Remove common markdown or text formatting
        text = text.strip()
        
        # Skip if it's clearly documentation/explanation
        if any(text.lower().startswith(word) for word in [
            'this command', 'the command', 'explanation:', 'note:', 'warning:', 'example:'
        ]):
            return False
        
        # Common shell command patterns
        command_indicators = [
            # Common Linux commands
            text.startswith(('ls ', 'cd ', 'mkdir ', 'rm ', 'cp ', 'mv ', 'cat ', 'grep ', 'find ', 'ps ', 'kill ', 'pkill ')),
            text.startswith(('sudo ', 'chmod ', 'chown ', 'tar ', 'zip ', 'unzip ', 'wget ', 'curl ', 'ssh ', 'scp ')),
            text.startswith(('git ', 'docker ', 'systemctl ', 'service ', 'mount ', 'umount ', 'df ', 'du ', 'top ', 'htop ')),
            # Pipe operations
            ' | ' in text,
            # Redirection
            ' > ' in text or ' >> ' in text or ' < ' in text,
            # Command chaining
            ' && ' in text or ' || ' in text or '; ' in text,
        ]
        
        return any(command_indicators) and len(text.split()) >= 1

    def _execute_command(self, command: str, output_name: str) -> None:
        """Execute a shell command and display the result.
        
        Args:
            command: The command to execute
            output_name: The name of the output for logging
        """
        try:
            print(f"\n🚀 Executing: {command}")
            print("=" * 50)
            
            # Execute the command
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=60  # 60 second timeout
            )
            
            # Display output
            if result.stdout:
                print("📤 Output:")
                print(result.stdout)
            
            if result.stderr:
                print("⚠️  Errors/Warnings:")
                print(result.stderr)
            
            print(f"✅ Exit code: {result.returncode}")
            print("=" * 50)
            
            # Log the execution
            self.logger.info(json.dumps({
                "log_message": "Command executed via auto-execution",
                "output_name": output_name,
                "command": command,
                "exit_code": result.returncode,
                "success": result.returncode == 0
            }))
            
        except subprocess.TimeoutExpired:
            print("❌ Command timed out after 60 seconds")
            self.logger.error(json.dumps({
                "log_message": "Command execution timeout",
                "output_name": output_name,
                "command": command
            }))
        except Exception as e:
            print(f"❌ Error executing command: {str(e)}")
            self.logger.error(json.dumps({
                "log_message": "Command execution error",
                "output_name": output_name,
                "command": command,
                "error": str(e)
            }))
