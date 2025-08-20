"""
Configuration module for AskAI CLI application.
Handles loading of user configuration from YAML files.
"""

# Standard library imports
import os

# Third-party imports
import yaml

CONFIG_PATH = os.path.expanduser("~/.askai_config.yml")

def load_config():
    """
    Load and parse the YAML configuration file.

    Returns:
        dict: The parsed configuration as a dictionary

    Raises:
        FileNotFoundError: If the configuration file doesn't exist
    """
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
