"""
Common utilities and functions shared across the output module.
"""

import codecs


def unescape_string(text: str) -> str:
    """Properly handle escaped characters in the content.
    
    This converts escaped sequences like \\n to actual newlines,
    which is especially important for HTML, CSS, and JS files.
    
    Args:
        text: The text to unescape
        
    Returns:
        str: The unescaped text with proper newlines and special characters
    """
    if not text:
        return text
    
    # Quick check if this content appears to need unescaping
    needs_unescaping = False
    escape_indicators = ['\\n', '\\t', '\\"', "\\'", '\\\\', '\\r']

    for indicator in escape_indicators:
        if indicator in text:
            needs_unescaping = True
            break

    if not needs_unescaping:
        return text
    
    # Count literal vs escaped newlines to make better decision
    literal_newline_count = text.count('\n') 
    escaped_newline_count = text.count('\\n')
    
    # If there are few escaped newlines compared to literal ones, this might be a false positive
    # (e.g., in CSS when we have selectors with \n in them or code examples)
    if escaped_newline_count > 0 and literal_newline_count < escaped_newline_count * 2:
        try:
            # Standard python unescaping - handles \n, \t, etc.
            # but will not apply if it causes syntax errors
            try:
                # Try python's built-in string_escape decoding first
                # This is the safest way to handle escape sequences
                result = codecs.escape_decode(bytes(text, "utf-8"))[0]
                
                # Only use this result if it successfully unescaped something
                if '\n' in result and result != text:
                    return result
            except (UnicodeDecodeError, AttributeError):
                pass
            
            # Manual replacement of common escape sequences
            result = text
            
            # Handle escape sequences in order of specificity (longer sequences first)
            replacements = [
                ('\\\\n', '\\n'),  # Handle double-escaped newlines
                ('\\\\t', '\\t'),  # Handle double-escaped tabs
                ('\\\\r', '\\r'),  # Handle double-escaped carriage returns
                ('\\n', '\n'),     # newline
                ('\\t', '\t'),     # tab
                ('\\"', '"'),      # double quote
                ("\\'", "'"),      # single quote
                ('\\\\', '\\'),    # backslash
                ('\\r', '\r'),     # carriage return
                ('\\b', '\b'),     # backspace
                ('\\f', '\f'),     # form feed
            ]
            
            for old, new in replacements:
                result = result.replace(old, new)
            
            # Check if we actually made changes
            if result != text:
                return result
                
        except Exception:
            pass  # If anything goes wrong, return the original
    
    # If we get here, either we didn't need to unescape or unescaping failed
    return text


def looks_like_command(text: str) -> bool:
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
        text.startswith((
            'ls ', 'cd ', 'mkdir ', 'rm ', 'cp ', 'mv ', 
            'cat ', 'grep ', 'find ', 'ps ', 'kill ', 'pkill '
        )),
        text.startswith((
            'sudo ', 'chmod ', 'chown ', 'tar ', 'zip ', 'unzip ', 
            'wget ', 'curl ', 'ssh ', 'scp '
        )),
        text.startswith((
            'git ', 'docker ', 'systemctl ', 'service ', 
            'mount ', 'umount ', 'df ', 'du ', 'top ', 'htop '
        )),
        # Pipe operations
        ' | ' in text,
        # Redirection
        ' > ' in text or ' >> ' in text or ' < ' in text,
        # Command chaining
        ' && ' in text or ' || ' in text or '; ' in text,
    ]
    
    return any(command_indicators) and len(text.split()) >= 1


def find_largest_match(matches, min_length=0):
    """Find the largest match in a list of regex matches.
    
    Args:
        matches: List of regex match strings
        min_length: Minimum length to consider a valid match
        
    Returns:
        str: The largest match, or None if no match meets the minimum length
    """
    if not matches:
        return None
        
    largest = max(matches, key=len)
    return largest if len(largest) > min_length else None
