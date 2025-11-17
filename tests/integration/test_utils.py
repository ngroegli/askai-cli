"""
Utilities for integration testing of askai-cli.
"""
import os
import subprocess
import sys
from typing import List, Tuple, Optional, Any
import re

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
CLI_SCRIPT = os.path.join(PROJECT_ROOT, "askai.sh")


def run_cli_command(args: List[str], input_text: Optional[str] = None) -> Tuple[str, str, int]:
    """
    Run the askai CLI with the given arguments and optional input.

    Args:
        args: Command line arguments to pass to askai
        input_text: Optional input to provide to the command via stdin

    Returns:
        Tuple of (stdout, stderr, return_code)
    """
    # Create a new environment with the correct PYTHONPATH
    env = os.environ.copy()

    # Set up the Python path to include the project root and python directory
    python_path = f"{PROJECT_ROOT}"
    if 'PYTHONPATH' in env:
        python_path = f"{python_path}:{env['PYTHONPATH']}"
    env['PYTHONPATH'] = python_path

    # Set testing environment variable to disable spinner animation
    env['ASKAI_TESTING'] = 'true'

    # Determine the correct Python executable to use
    # If we're in a virtual environment, use that Python, otherwise use sys.executable
    python_executable = sys.executable

    # Check if we're running from a virtual environment and it's available
    venv_python = os.path.join(PROJECT_ROOT, "venv", "bin", "python")
    if os.path.exists(venv_python):
        # If venv exists and we're not already using it, use it
        if not python_executable.startswith(os.path.join(PROJECT_ROOT, "venv")):
            python_executable = venv_python

    # Use the shell script which handles the Python path correctly
    cmd = [CLI_SCRIPT] + args

    # Set up the subprocess parameters
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE if input_text else None,
        text=True,
        env=env,
        cwd=PROJECT_ROOT  # Run from project root directory
    )

    # Run the command and capture output
    stdout, stderr = process.communicate(input=input_text)
    return_code = process.returncode

    return stdout, stderr, return_code


def verify_output_contains(output: str, expected_patterns: List[str]) -> Tuple[bool, List[str]]:
    """
    Verify that output contains all expected patterns.

    Args:
        output: The output text to verify
        expected_patterns: List of patterns (strings or regex patterns) to check for

    Returns:
        Tuple of (success, list of missing patterns)
    """
    missing = []
    for pattern in expected_patterns:
        if not re.search(pattern, output, re.MULTILINE):
            missing.append(pattern)

    return len(missing) == 0, missing


def verify_basic_json_format(output: str) -> Tuple[bool, str]:
    """
    Perform basic JSON format validation without parsing.

    This checks for basic JSON structure patterns and can handle
    output with prefixes/suffixes around the JSON content.
    It's designed to be fault-tolerant and detect JSON even when
    embedded within other text.

    Args:
        output: The output text to check for JSON format

    Returns:
        Tuple of (is_json_like, reason)
    """
    if not output or not output.strip():
        return False, "Empty output"

    # First, look for complete JSON objects or arrays anywhere in the text
    # This handles cases where JSON is embedded within other content

    # Try to find JSON object patterns (more comprehensive)
    json_object_patterns = [
        r'\{[^{}]*"[^"]+"\s*:\s*[^{}]*\}',  # Simple object with at least one key-value
        r'\{[^{}]*"[^"]+"\s*:\s*"[^"]*"[^{}]*\}',  # Object with string value
        r'\{[^{}]*"[^"]+"\s*:\s*\[[^\]]*\][^{}]*\}',  # Object with array value
        r'\{[^{}]*"[^"]+"\s*:\s*\{[^{}]*\}[^{}]*\}',  # Object with nested object
        r'\{[^{}]*"[^"]+"\s*:\s*(?:true|false|null|\d+)[^{}]*\}',  # Object with literal value
    ]

    # Try to find JSON array patterns
    json_array_patterns = [
        r'\[\s*"[^"]*"[^\]]*\]',  # Array with string elements
        r'\[\s*\{[^{}]*\}[^\]]*\]',  # Array with object elements
        r'\[\s*\d+[^\]]*\]',  # Array with numeric elements
        r'\[\s*(?:true|false|null)[^\]]*\]',  # Array with literal elements
    ]

    # Check for multiline JSON structures (common in real output)
    multiline_json_patterns = [
        r'\{\s*\n\s*"[^"]+"\s*:\s*\[',  # Multi-line object starting with array
        r'\{\s*\n\s*"[^"]+"\s*:\s*"',   # Multi-line object starting with string
        r'\{\s*\n\s*"[^"]+"\s*:\s*\{',  # Multi-line object with nested object
    ]

    # Combine all patterns
    all_patterns = json_object_patterns + json_array_patterns + multiline_json_patterns

    for pattern in all_patterns:
        if re.search(pattern, output, re.DOTALL | re.MULTILINE):
            return True, f"Found JSON structure matching pattern: {pattern[:50]}..."

    # Fallback: Look for basic JSON structure indicators
    # This catches cases where the above patterns might be too strict
    has_json_brackets = bool(re.search(r'\{.*\}|\[.*\]', output, re.DOTALL))
    has_quoted_keys = bool(re.search(r'"[^"]+"\s*:', output))
    has_json_values = bool(re.search(r':\s*(?:"[^"]*"|\d+|true|false|null|\[|\{)', output))

    if has_json_brackets and has_quoted_keys and has_json_values:
        return True, "Found JSON-like structure with brackets, quoted keys, and values"

    # Even more lenient check for obvious JSON content
    if has_json_brackets and has_quoted_keys:
        return True, "Found basic JSON structure with brackets and quoted keys"

    # Final check: look for any structure that looks like it could be JSON
    if re.search(r'\{\s*"', output) or re.search(r'\[\s*["{]', output):
        return True, "Found minimal JSON-like structure"

    return False, "No JSON structure detected in output"


class TestResult:
    """Class to track and report test results."""

    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""
        self.details = {}

    def set_passed(self, message: str = "Test passed"):
        self.passed = True
        self.message = message

    def set_failed(self, message: str):
        self.passed = False
        self.message = message

    def add_detail(self, key: str, value: Any):
        self.details[key] = value

    def __str__(self):
        # ANSI color codes
        GREEN = "\033[92m"  # Bright green
        RED = "\033[91m"    # Bright red
        RESET = "\033[0m"   # Reset color

        status = f"{GREEN}PASS{RESET}" if self.passed else f"{RED}FAIL{RESET}"
        result = f"[{status}] {self.name}: {self.message}"

        if self.details:
            detail_str = "\n".join(f"  {k}: {v}" for k, v in self.details.items())
            result += f"\nDetails:\n{detail_str}"
        return result
