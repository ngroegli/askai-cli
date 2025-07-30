"""
Output processing and handling module.
Manages different output formats and file writing.
"""

import json
import re
import subprocess
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
            response: The AI response text
            args: Command line arguments
            system_outputs: Optional list of SystemOutput objects for auto-execution
        
        Returns:
            bool: True if output was handled and program should exit, False otherwise
        """
        # First, handle normal output display
        should_exit = False
        
        if args.output:
            self.logger.info(json.dumps({
                "log_message": "Writing response to output file", 
                "output_file": args.output
            }))
            self.write_to_file(args.output, response)
            print(f"Response written to {args.output}")
            should_exit = True
        elif args.format == "md" and not args.plain_md:
            self.logger.info(json.dumps({"log_message": "Rendering response as markdown"}))
            self.render_markdown(response)
        else:
            self.logger.info(json.dumps({"log_message": "Printing response as raw text"}))
            print(response)
        
        # After displaying output, handle auto-execution of code outputs if system outputs are provided
        if system_outputs and not should_exit:
            self._handle_auto_execution(response, system_outputs)
        
        return should_exit

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
