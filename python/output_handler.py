"""
Output processing and handling module.
Manages different output formats and file writing.
"""

import json
from rich.console import Console
from rich.markdown import Markdown


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

    def handle_output(self, response, args):
        """Handle the output of the AI response based on arguments.
        
        Returns:
            bool: True if output was handled and program should exit, False otherwise
        """
        if args.output:
            self.logger.info(json.dumps({
                "log_message": "Writing response to output file", 
                "output_file": args.output
            }))
            self.write_to_file(args.output, response)
            print(f"Response written to {args.output}")
            return True

        if args.format == "md" and not args.plain_md:
            self.logger.info(json.dumps({"log_message": "Rendering response as markdown"}))
            self.render_markdown(response)
            return True

        self.logger.info(json.dumps({"log_message": "Printing response as raw text"}))
        print(response)
        return False
