import os
import sys
import itertools
import time
import subprocess
from tqdm import tqdm

def write_to_file(path, content):
    with open(path, "w") as f:
        f.write(content)

def clean_response_text(text):
    return text.strip()

def tqdm_spinner(stop_event):
    """Displays a rotating spinner using tqdm."""
    with tqdm(total=1, bar_format="{desc} {bar}") as pbar:
        spinner_cycle = itertools.cycle(['|', '/', '-', '\\'])
        while not stop_event.is_set():
            pbar.set_description_str(f"Thinking {next(spinner_cycle)}")
            time.sleep(0.1)


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


def get_system_context(system_name, base_path):
    """Loads system-specific context file from the systems directory."""
    systems_dir = os.path.join(base_path, "systems")
    system_file = os.path.join(systems_dir, system_name)

    if os.path.exists(system_file):
        with open(system_file, "r") as f:
            return f.read()
    print(f"System file {system_file} not found.")
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
