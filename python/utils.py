import os
import sys
import itertools
import time
import subprocess
from tqdm import tqdm
from rich.console import Console
from rich.markdown import Markdown
from termcolor import colored, cprint


def write_to_file(path, content):
    with open(path, "w") as f:
        f.write(content)

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

def get_system_context(system_name, base_path):
    """Loads system-specific context file from the systems directory."""
    systems_dir = os.path.join(base_path, "systems")
    system_file = os.path.join(systems_dir, "{0}.md".format(system_name))

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

def list_system_files(base_path):
    """Lists all available system files"""
    systems_dir = os.path.join(base_path, "systems")
    
    if not os.path.isdir(systems_dir):
        print(f"No 'systems' directory found at {systems_dir}")
        sys.exit(1)

    system_files = sorted(os.listdir(systems_dir))

    if not system_files:
        print("No system files found.")
    else:
        print("\nAvailable system files:\n")
        for file in system_files:
            if not file.startswith("_"):
                print(f" - {file.removesuffix(".md")}")

def view_system_file(base_path, system):
    """Prints system files content"""
    systems_dir = os.path.join(base_path, "systems")
    system = "{0}.md".format(system)
    
    if not os.path.isdir(systems_dir):
        print(f"No 'systems' directory found at {systems_dir}")
        sys.exit(1)

    system_files = sorted(os.listdir(systems_dir))

    if not system_files:
        print("No system files found.")
    else:
        for file in system_files:
            if file == system:
                with open(os.path.join(systems_dir, system), "r") as f:
                    print(f.read())
                    sys.exit(0)
        print("System file does not exists")

def render_markdown(markdown_content):
    """This prints the markdown text as rendered markdown to the console"""
    console = Console()
    md = Markdown(markdown_content)
    console.print(md)

def print_error_or_warnings(text,warning_only=False):
    color = "red"

    if warning_only:
        color = "light_yellow"

    cprint(text, color)
    