"""
General utility functions for the AskAI CLI application.
Contains core utilities for input handling, command execution, and formatting.
"""

import os
import sys
import itertools
import time
import subprocess
from tqdm import tqdm
from termcolor import colored, cprint


def tqdm_spinner(stop_event):
    """Displays a rotating spinner using tqdm."""
    thinking_color = "light_cyan"
    result_color = "green"

    with tqdm(total=1, bar_format="{desc} {bar}", leave=False) as pbar:
        spinner_cycle = itertools.cycle(['|', '/', '-', '\\'])
        while not stop_event.is_set():
            pbar.set_description_str(colored(f"Thinking {next(spinner_cycle)}", thinking_color))
            time.sleep(0.1)
        pbar.close()
        cprint("HERE THE RESULT:", result_color)


def get_piped_input():
    """Reads piped stdin input, if available."""
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return None


def get_file_input(file_path):
    """Reads content from a file if it exists."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    print(f"File {file_path} does not exist.")
    return None


def build_format_instruction(format_type):
    """Returns AI instruction based on the desired response format."""
    return {
        "rawtext": "Please provide your response as plain text.",
        "md": "Please format the response as GitHub-flavored Markdown.",
        "json": "Please respond with a valid JSON structure containing your answer."
    }.get(format_type, "Please provide your response as plain text.")


def capture_command_output(command):
    """Run a shell command and capture output, return stdout as string."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Command failed: {result.stderr}")
    return result.stdout


def print_error_or_warnings(text, warning_only=False):
    """Print error or warning messages with appropriate colors."""
    color = "red"
    if warning_only:
        color = "light_yellow"
    cprint(text, color)
    