"""
FileWriter class for writing various file types with proper formatting.

This class consolidates the functionality of specialized writers into a single class
that handles writing content with appropriate formatting based on file type.
"""

import os
import re
import json
import traceback
from pathlib import Path
from typing import Optional, Dict, List, Union


class FileWriter:
    """FileWriter that handles writing content to files with proper formatting for each file type."""

    def __init__(self, output_dir: Optional[str] = None, logger=None, expose_internals: bool = False):
        """Initialize the FileWriter.

        Args:
            output_dir: Optional output directory for files
            logger: Optional logger instance
            expose_internals: Allow access to protected methods for testing
        """
        self.output_dir = output_dir
        self.logger = logger
        self.expose_internals = expose_internals

    def clean_content_for_testing(self, content: str, extension: str) -> str:
        """Public wrapper for _clean_content for testing purposes.

        Args:
            content: Content to clean
            extension: File extension (including the dot)

        Returns:
            str: Cleaned content
        """
        return self._clean_content(content, extension)

    def process_and_write_for_testing(
        self, content: str, file_path: str, extension: str,
        additional_params: Optional[Dict] = None
    ) -> bool:
        """Public wrapper for _process_and_write_file for testing purposes.

        Args:
            content: Content to write
            file_path: Path where to write the file
            extension: File extension (including the dot)
            additional_params: Additional parameters for specific file types

        Returns:
            bool: True if successful, False otherwise
        """
        return self._process_and_write_file(content, file_path, extension, additional_params)

    def write(self, content: str, file_path: str) -> bool:
        """Write content to a file.

        Args:
            content: Content to write
            file_path: Path where to write the file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure parent directory exists
            path_obj = Path(file_path)
            path_obj.parent.mkdir(parents=True, exist_ok=True)

            # Sanitize content to handle potential encoding issues
            if content is None:
                content = ""
                if self.logger:
                    self.logger.warning("Null content provided for %s, using empty string", file_path)

            # Handle non-string content
            if not isinstance(content, str):
                content = str(content)
                if self.logger:
                    self.logger.warning("Non-string content converted for %s", file_path)

            # Log content size for debugging
            content_size = len(content)
            if self.logger and content_size > 1000000:  # 1MB
                self.logger.warning("Very large content (%.2fMB) for %s", content_size/1000000, file_path)

            # Write the file with explicit encoding
            with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
                f.write(content)

            # Verify the file was written
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                if self.logger:
                    self.logger.info("Content written to %s (%s chars, %s bytes)", file_path, content_size, file_size)
                return True
            if self.logger:
                self.logger.error("File %s was not created", file_path)
            return False

        except UnicodeEncodeError as ue:
            # Special handling for Unicode errors
            if self.logger:
                self.logger.error("Unicode encoding error writing to %s: %s", file_path, str(ue))
                self.logger.info("Attempting to write with explicit ascii encoding and character replacement")

            try:
                # Try again with ASCII encoding and character replacement
                with open(file_path, 'w', encoding='ascii', errors='replace') as f:
                    f.write(content)
                if self.logger:
                    self.logger.info("Successfully wrote file with ASCII encoding: %s", file_path)
                return True
            except (IOError, OSError) as e2:
                if self.logger:
                    self.logger.error("Second attempt to write file failed due to I/O error: %s", str(e2))
                return False
            except (ValueError, TypeError, RuntimeError) as e2:
                if self.logger:
                    self.logger.error("Second attempt to write file failed: %s", str(e2))
                return False

        except (IOError, OSError) as e:
            if self.logger:
                self.logger.error("I/O error writing to %s: %s", file_path, str(e))
                self.logger.debug("Error details: %s", traceback.format_exc())
            return False
        except (ValueError, TypeError, RuntimeError) as e:
            if self.logger:
                self.logger.error("Unexpected error writing to %s: %s", file_path, str(e))
                # Log more details about the error
                self.logger.debug("Error details: %s", traceback.format_exc())
            return False

    def write_by_extension(self, content: str, file_path: str,
                        additional_params: Optional[Dict] = None) -> bool:
        """Write content based on file extension with appropriate formatting.

        Args:
            content: Content to write
            file_path: Path where to write the file
            additional_params: Additional parameters for specific file types

        Returns:
            bool: True if successful, False otherwise
        """
        # Safety check for None or empty content
        if content is None:
            if self.logger:
                self.logger.error(f"Null content provided for {file_path}")
                # Write empty file instead of failing completely
                return self.write("", file_path)
            return False

        # Make sure content is a string
        if not isinstance(content, str):
            try:
                content = str(content)
                if self.logger:
                    self.logger.warning(f"Non-string content converted for {file_path}")
            except (ValueError, TypeError) as e:
                if self.logger:
                    self.logger.error("Failed to convert content to string: %s", str(e))
                return False
            except AttributeError as e:
                if self.logger:
                    self.logger.error("Unexpected error converting content to string: %s", str(e))
                return False

        # Make sure we have actual content to write
        if not content.strip():
            if self.logger:
                self.logger.warning(f"Empty content provided for {file_path}, writing empty file")

        extension = os.path.splitext(file_path)[1].lower()
        additional_params = additional_params or {}

        # Process content based on file extension
        return self._process_and_write_file(
            content=content,
            file_path=file_path,
            extension=extension,
            additional_params=additional_params
        )

    def _process_and_write_file(self, content: str, file_path: str,
                          extension: str, additional_params: Optional[Dict] = None) -> bool:
        """Process content based on file type and write to file.

        This unified method replaces multiple file-type specific methods,
        applying appropriate cleaning and formatting for each file type.

        Args:
            content: Content to write
            file_path: Path where to write the file
            extension: File extension (including the dot)
            additional_params: Additional parameters for specific file types

        Returns:
            bool: True if successful, False otherwise
        """
        additional_params = additional_params or {}

        # 1. Clean and format content based on file type
        cleaned_content = self._clean_content(content, extension)

        # 2. Make sure file path has appropriate extension if not already present
        file_lower = file_path.lower()
        if not file_lower.endswith(extension):
            # For special cases where we have alternate extensions
            if extension in ['.md', '.markdown'] and not file_lower.endswith(('.md', '.markdown')):
                file_path += '.md'
            elif extension in ['.html', '.htm'] and not file_lower.endswith(('.html', '.htm')):
                file_path += '.html'
            else:
                # General case - just append the extension
                file_path += extension

        # 3. Format the content based on file type
        formatted_content = cleaned_content

        # Type-specific formatting
        if extension in ['.md', '.markdown']:
            # Handle markdown
            front_matter = additional_params.get('front_matter')
            formatted_content = self._format_markdown(cleaned_content, front_matter)

        elif extension in ['.html', '.htm']:
            # Handle HTML with references
            css_path = additional_params.get('css_path')
            js_path = additional_params.get('js_path')
            formatted_content = self._validate_html_references(cleaned_content, css_path, js_path)

        elif extension == '.css':
            # Add CSS header
            header = "/*\n * Generated CSS file\n */\n\n"
            formatted_content = header + cleaned_content.strip()

        elif extension == '.js':
            # Format JavaScript
            formatted_content = self._format_js_content(cleaned_content)

        elif extension == '.json':
            # Handle JSON formatting
            try:
                # Parse JSON if it's a string
                if isinstance(content, str):
                    try:
                        content_obj = self._parse_json_content(content)
                    except json.JSONDecodeError as parse_error:
                        if self.logger:
                            self.logger.error(f"Failed to parse JSON content: {str(parse_error)}")
                        return False
                else:
                    content_obj = content

                # Format with or without indentation
                pretty = additional_params.get('pretty', True)
                formatted_content = json.dumps(content_obj,
                                           indent=2 if pretty else None,
                                           sort_keys=False)
            except (TypeError, ValueError) as e:
                if self.logger:
                    self.logger.error(f"Failed to format JSON: {str(e)}")
                return False

        # 4. Write the formatted content to the file
        return self.write(formatted_content, file_path)

    def _clean_content(self, content: str, extension: str) -> str:
        """Clean content based on file type, removing escape characters and code blocks.

        Args:
            content: Content to clean
            extension: File extension (including the dot)

        Returns:
            str: Cleaned content
        """
        if not isinstance(content, str):
            return str(content)

        # For any extension, try to remove generic code block markers
        content = re.sub(r'^```\w*\s*', '', content)
        content = re.sub(r'\s*```$', '', content)

        # Try to decode JSON encoded content
        try:
            if content.strip().startswith('"') and content.strip().endswith('"'):
                try:
                    decoded = json.loads(content)
                    if isinstance(decoded, str):
                        if self.logger:
                            self.logger.info("Decoded JSON-encoded content")
                        content = decoded
                except json.JSONDecodeError:
                    # Not valid JSON, continue with regular cleaning
                    pass
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            if self.logger:
                self.logger.debug("Error while checking for JSON-encoded content: %s", str(e))
            # Continue with regular processing regardless of error

        # Fix the issue where a real newline followed by 'n' should have been a '\n' escape
        # This pattern matches a newline followed by 'n' at the beginning of a line
        # We use a more generic approach to catch both 'n ' and 'n' followed by any non-whitespace char
        content = re.sub(r'(\n|\r\n)n(\S)', r'\1\2', content)

        # Handle double-escaped newlines (\\n) first - they should become single escaped (\n) before further processing
        content = content.replace('\\\\n', '\\n')

        # Now proceed with regular escape sequence handling
        cleaned = content.replace('\\n', '\n')
        cleaned = cleaned.replace('\\"', '"')
        cleaned = cleaned.replace("\\'", "'")
        cleaned = cleaned.replace('\\\\', '\\')
        cleaned = cleaned.replace('\\t', '\t')
        cleaned = cleaned.replace('\\r', '\r')

        # Enhanced check for lines that start with 'n' in CSS files
        lines = cleaned.split('\n')
        fixed_lines = []

        # CSS specific selectors that commonly follow 'n' when incorrectly processed
        css_selectors = [
            'html', 'body', 'div', 'span', 'a', 'p', 'ul', 'ol', 'li',
            'header', 'footer', 'nav', 'section', 'article', 'aside',
            'main', 'form', 'input', 'button', 'img', 'table', 'tr', 'td', 'th'
        ]

        for line in lines:
            stripped_line = line.strip()
            # Check for 'n' followed by space
            if stripped_line.startswith('n '):
                fixed_lines.append(line[line.find('n')+1:])
            # CSS file specific: check for 'n' followed by CSS selector
            elif extension == '.css' and stripped_line.startswith('n'):
                found_selector = False
                for selector in css_selectors:
                    if stripped_line.startswith('n' + selector) and (
                        len(stripped_line) == len('n' + selector) or
                        stripped_line[len('n' + selector)] in [' ', '{', '.', '#', ':', '[']
                    ):
                        # It's likely a CSS selector - remove the 'n'
                        fixed_lines.append(line[line.find('n')+1:])
                        found_selector = True
                        break

                if not found_selector:
                    # No CSS selector match, keep the line as is
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        cleaned = '\n'.join(fixed_lines)

        # Remove JSON-style unicode escapes
        cleaned = re.sub(r'\\u([0-9a-fA-F]{4})',
                       lambda m: chr(int(m.group(1), 16)),
                       cleaned)

        # Fix improper HTML entity escapes if it appears to be HTML
        if extension in ['.html', '.htm'] or re.search(r'<[a-zA-Z]+[^>]*>', cleaned):
            cleaned = re.sub(r'&amp;([a-zA-Z]+);', r'&\1;', cleaned)

        if self.logger and cleaned != content:
            self.logger.info(f"Cleaned up escaped characters in {extension} content")

        return cleaned

    def get_output_directory(self, suggested_path: Optional[str] = None) -> Optional[str]:
        """Get the directory where files should be written, with user interaction.

        Args:
            suggested_path: Optional suggested path to use

        Returns:
            str: Directory path, or None if user cancelled
        """
        print("\n📁 File Output Location")
        print("=" * 50)
        print("The system will create files automatically.")
        print("Hint: Use '.' for current directory or specify a path like './my-website'")

        if suggested_path:
            print(f"Suggested path: {suggested_path}")

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
                except (IOError, OSError, PermissionError) as e:
                    print(f"❌ Error creating directory: {str(e)}")
                    print("Using current directory instead.")
                    return str(Path(".").resolve())
            else:
                print("Using current directory instead.")
                return str(Path(".").resolve())

    # Private helper methods for formatting content

    def _format_markdown(self, markdown_content: str, front_matter: Optional[Dict] = None) -> str:
        """Format Markdown content for proper output.

        Args:
            markdown_content: The Markdown content to format
            front_matter: Optional YAML front matter to include

        Returns:
            str: Formatted Markdown content
        """
        # Remove markdown code block markers if present
        markdown_content = re.sub(r'^```md\s*|^```markdown\s*', '', markdown_content)
        markdown_content = re.sub(r'\s*```$', '', markdown_content)

        # Ensure the content starts with a title if not present
        if not re.match(r'^#\s+', markdown_content):
            # Try to extract a title from the first paragraph or line
            lines = markdown_content.split('\n')
            first_line = next((line for line in lines if line.strip()), "Document")

            # Remove any markdown formatting from the first line
            title = re.sub(r'[*_`#]', '', first_line).strip()

            # Limit title length
            if len(title) > 50:
                title = title[:47] + "..."

            # Add the title as H1
            markdown_content = f"# {title}\n\n{markdown_content}"

            if self.logger:
                self.logger.info(f"Added missing title to markdown: '{title}'")

        # Add front matter if provided
        if front_matter and isinstance(front_matter, dict):
            # Convert front matter to YAML format
            yaml_front_matter = "---\n"
            for key, value in front_matter.items():
                if isinstance(value, list):
                    yaml_front_matter += f"{key}:\n"
                    for item in value:
                        yaml_front_matter += f"  - {item}\n"
                else:
                    yaml_front_matter += f"{key}: {value}\n"
            yaml_front_matter += "---\n\n"

            # Check if the markdown already has front matter
            if not re.match(r'^---\s*\n', markdown_content):
                markdown_content = yaml_front_matter + markdown_content
                if self.logger:
                    self.logger.info("Added YAML front matter to markdown")

        # Ensure there's a blank line at the end of the file
        if not markdown_content.endswith('\n\n'):
            if markdown_content.endswith('\n'):
                markdown_content += '\n'
            else:
                markdown_content += '\n\n'

        return markdown_content

    def _validate_html_references(self, html_content: str, css_path: Optional[str] = None,
                               js_path: Optional[str] = None) -> str:
        """Validate and fix HTML file references to match output filenames.

        Args:
            html_content: The HTML content to validate
            css_path: Optional path to CSS file
            js_path: Optional path to JS file

        Returns:
            str: Validated HTML content with correct file references
        """
        # Make sure HTML has proper structure
        if not re.search(r'<html[^>]*>', html_content, re.IGNORECASE):
            html_content = (
                f'<!DOCTYPE html>\n'
                '<html lang="en">\n'
                '<head>\n'
                '<meta charset="UTF-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                '<title>Generated Page</title>\n'
                '</head>\n'
                '<body>\n'
                f'{html_content}\n'
                '</body>\n'
                '</html>'
            )
            if self.logger:
                self.logger.info("Added HTML structure to content")

        # Ensure there's a head section
        if not re.search(r'<head[^>]*>', html_content, re.IGNORECASE):
            # Add a head section before the body
            body_start = html_content.find('<body')
            if body_start != -1:
                head_content = (
                    '<head>\n'
                    '<meta charset="UTF-8">\n'
                    '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                    '<title>Generated Page</title>\n'
                    '</head>\n'
                )
                html_content = html_content[:body_start] + head_content + html_content[body_start:]
                if self.logger:
                    self.logger.info("Added missing head section")

        # Fix CSS reference if found
        if css_path:
            # Extract just the filename without path
            css_filename = css_path.split('/')[-1]

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
                if self.logger:
                    self.logger.info(f"Updated CSS reference to: {css_filename}")
            else:
                # No CSS link found, add it to head
                head_end = html_content.find('</head>')
                if head_end != -1:
                    css_link = f'    <link rel="stylesheet" href="{css_filename}">\n'
                    html_content = html_content[:head_end] + css_link + html_content[head_end:]
                    if self.logger:
                        self.logger.info(f"Added CSS reference: {css_filename}")
                else:
                    # If no head end tag found, try to add before body
                    body_start = html_content.find('<body')
                    if body_start != -1:
                        head_with_css = (
                            '<head>\n'
                            f'    <link rel="stylesheet" href="{css_filename}">\n'
                            '</head>\n'
                        )
                        html_content = html_content[:body_start] + head_with_css + html_content[body_start:]
                        if self.logger:
                            self.logger.info(f"Added head with CSS reference: {css_filename}")
                    else:
                        # Last resort: prepend to the content
                        html_structure = (
                            f'<!DOCTYPE html>\n<html>\n<head>\n'
                            f'    <link rel="stylesheet" href="{css_filename}">\n'
                            f'</head>\n<body>\n{html_content}\n</body>\n</html>'
                        )
                        html_content = html_structure
                        if self.logger:
                            self.logger.info(f"Restructured HTML and added CSS reference: {css_filename}")

        # Fix JS reference if found
        if js_path:
            # Extract just the filename without path
            js_filename = js_path.split('/')[-1]

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
                if self.logger:
                    self.logger.info(f"Updated JS reference to: {js_filename}")
            else:
                # Try to add before closing head tag
                head_end = html_content.find('</head>')
                if head_end != -1:
                    script_tag = f'    <script src="{js_filename}" defer></script>\n'
                    html_content = html_content[:head_end] + script_tag + html_content[head_end:]
                    if self.logger:
                        self.logger.info(f"Added JS reference: {js_filename}")
                else:
                    # If no head end tag, try to add before body
                    body_start = html_content.find('<body')
                    if body_start != -1:
                        script_tag = f'<script src="{js_filename}" defer></script>\n'
                        html_content = html_content[:body_start] + script_tag + html_content[body_start:]
                        if self.logger:
                            self.logger.info(f"Added JS reference: {js_filename}")
                    else:
                        # Last resort: add at the end of the content
                        html_content = html_content + f'\n<script src="{js_filename}" defer></script>\n'
                        if self.logger:
                            self.logger.info(f"Added JS reference at end: {js_filename}")

        # Ensure we have a complete HTML document structure
        if not html_content.strip().lower().startswith('<!doctype'):
            if not html_content.strip().lower().startswith('<html'):
                html_content = f'<!DOCTYPE html>\n<html>\n{html_content}</html>'
                if self.logger:
                    self.logger.info("Added missing DOCTYPE and html tags")
            else:
                html_content = f'<!DOCTYPE html>\n{html_content}'
                if self.logger:
                    self.logger.info("Added missing DOCTYPE")

        # Ensure <head> comes before <body>
        head_pos = html_content.lower().find('<head')
        body_pos = html_content.lower().find('<body')

        if head_pos > body_pos and body_pos != -1 and head_pos != -1:
            # Extract the head content
            head_end = html_content.lower().find('</head>', head_pos)
            head_content = html_content[head_pos:head_end+7]

            # Remove the head from its current position
            html_content = html_content[:head_pos] + html_content[head_end+7:]

            # Insert it before body
            body_pos = html_content.lower().find('<body')  # Recalculate position
            html_content = html_content[:body_pos] + head_content + html_content[body_pos:]
            if self.logger:
                self.logger.info("Fixed HTML structure: moved head before body")

        # Format HTML indentation
        html_content = self._format_html_indentation(html_content)

        return html_content

    def _format_html_indentation(self, html_content: str) -> str:
        """Format HTML content with proper indentation.

        Args:
            html_content: HTML content to format

        Returns:
            str: Formatted HTML content with proper indentation
        """
        try:
            # Only attempt to reformat if there are HTML tags
            if not re.search(r'<[a-zA-Z]+[^>]*>', html_content):
                return html_content

            # Simple tags to look for
            block_tags = ['html', 'head', 'body', 'div', 'header', 'main', 'footer',
                          'section', 'article', 'nav', 'aside', 'form']

            lines = html_content.split('\n')
            indented_lines = []
            indent_level = 0

            for line in lines:
                # Skip empty lines
                stripped = line.strip()
                if not stripped:
                    indented_lines.append('')
                    continue

                # Check for closing tags that should decrease indent
                # Look for </tag> pattern
                closing_match = re.match(r'^\s*</([a-zA-Z]+)[^>]*>', stripped)
                if closing_match and closing_match.group(1).lower() in block_tags:
                    indent_level = max(0, indent_level - 1)  # Prevent negative indent

                # Add the line with proper indentation
                indented_lines.append('  ' * indent_level + stripped)

                # Check for opening tags that should increase indent
                # Look for <tag> or <tag attr="value"> patterns but not self-closing tags
                match = re.match(r'^\s*<([a-zA-Z]+)[^>]*>(?!</)', stripped)
                if match:
                    tag = match.group(1).lower()
                    if tag in block_tags and not '/' in stripped[-2:]:  # Not self-closing
                        indent_level += 1

            return '\n'.join(indented_lines)
        except (IndexError, ValueError, AttributeError) as e:
            # If indentation fails due to common parsing errors, just use the original content
            if self.logger:
                self.logger.debug("HTML indentation failed due to parsing error: %s", str(e))
            return html_content
        except (TypeError, RuntimeError) as e:
            # If indentation fails for any other reason, just use the original content
            if self.logger:
                self.logger.debug("HTML indentation failed due to unexpected error: %s", str(e))
            return html_content

    def _format_js_content(self, js_content: str) -> str:
        """Format JavaScript content for proper output.

        Args:
            js_content: The JavaScript content to format

        Returns:
            str: Formatted JavaScript content
        """
        # Remove script tags if present
        js_content = re.sub(r'<script[^>]*>(.*?)</script>', r'\1',
                           js_content, flags=re.DOTALL | re.IGNORECASE)

        # Cleanup common formatting issues

        # Ensure semicolons at the end of statements if not already there
        # This is a simple heuristic and won't catch all cases
        js_content = re.sub(r'(\w+|\)|\]|\})\s*$', r'\1;', js_content, flags=re.MULTILINE)

        # Fix missing semicolons before line breaks for common patterns
        js_content = re.sub(r'(\w+|\)|\]|\})\s*\n', r'\1;\n', js_content)

        # Don't add semicolons after blocks or if one already exists
        js_content = re.sub(r';\s*;', r';', js_content)
        js_content = re.sub(r'\}\s*;', r'}', js_content)

        # Ensure document.addEventListener for DOMContentLoaded if interacting with DOM
        has_dom_methods = re.search(
            r'document\.getElementById|document\.querySelector|document\.getElement',
            js_content, re.IGNORECASE
        )
        has_dom_loaded = re.search(r'DOMContentLoaded', js_content, re.IGNORECASE)

        if has_dom_methods and not has_dom_loaded:
            # Check if the content is already wrapped in a function or event listener
            if not re.search(r'^\s*\(\s*function|window\.onload|addEventListener', js_content.lstrip()):
                # Wrap the content in DOMContentLoaded event listener
                js_content = (
                    "document.addEventListener('DOMContentLoaded', function() {\n" +
                    self._indent_code(js_content) +
                    "\n});"
                )
                if self.logger:
                    self.logger.info("Added DOMContentLoaded wrapper for DOM interactions")

        # Add use strict if not present
        if not re.search(r"'use strict'|\"use strict\"", js_content):
            # If there's a DOMContentLoaded wrapper, add use strict inside it
            if re.search(r"document\.addEventListener\('DOMContentLoaded',", js_content):
                js_content = re.sub(
                    r"(document\.addEventListener\('DOMContentLoaded',\s*function\(\)\s*\{)\s*",
                    r"\1\n  'use strict';\n  ",
                    js_content
                )
            else:
                # Otherwise add it at the top
                js_content = "'use strict';\n\n" + js_content

            if self.logger:
                self.logger.info("Added 'use strict' directive")

        return js_content

    def _indent_code(self, code: str, spaces: int = 2) -> str:
        """Indent code by the specified number of spaces.

        Args:
            code: Code to indent
            spaces: Number of spaces for indentation

        Returns:
            str: Indented code
        """
        indent = ' ' * spaces
        return indent + code.replace('\n', '\n' + indent)

    def _parse_json_content(self, content: str) -> Union[Dict, List]:
        """Parse JSON string content into a Python object.

        Args:
            content: JSON content as a string

        Returns:
            Union[Dict, List]: Parsed JSON as a Python object

        Raises:
            json.JSONDecodeError: If the content cannot be parsed as JSON
        """
        # Remove code block markers if present
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'\s*```$', '', content)

        # Try to parse the JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to fix common JSON errors
            content = self._fix_common_json_errors(content)
            return json.loads(content)  # If this fails, let the error propagate

    def _fix_common_json_errors(self, content: str) -> str:
        """Fix common JSON formatting errors.

        Args:
            content: JSON content to fix

        Returns:
            str: Fixed JSON content
        """
        # Replace single quotes with double quotes (except within strings)
        # This is a simplistic approach and won't handle all cases correctly
        content = re.sub(r"(?<!\")\'(?!\")", '"', content)

        # Fix missing quotes around property names
        content = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', content)

        # Replace trailing commas in arrays and objects
        content = re.sub(r',\s*}', '}', content)
        content = re.sub(r',\s*]', ']', content)

        if self.logger:
            self.logger.info("Fixed common JSON formatting errors")

        return content
