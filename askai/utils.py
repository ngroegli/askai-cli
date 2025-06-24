import subprocess
import os

def write_to_file(path, content):
    with open(path, "w") as f:
        f.write(content)

def clean_response_text(text):
    return text.strip()

def capture_command_output(command):
    """Run a shell command and capture output, return stdout as string."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Command failed: {result.stderr}")
    return result.stdout
