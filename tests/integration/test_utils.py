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
    
    # Use the Python interpreter directly with the correct module
    cmd = [sys.executable, os.path.join(PROJECT_ROOT, "python/askai.py")] + args
    
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
