"""
Configuration module for AskAI CLI application.
Handles loading of user configuration from YAML files.
Supports separate test configuration for integration and unit tests.
"""

# Standard library imports
import os
import shutil

# Third-party imports
import yaml

CONFIG_PATH = os.path.expanduser("~/.askai_config.yml")
TEST_CONFIG_PATH = os.path.expanduser("~/.askai_config_test.yml")

def is_test_environment():
    """
    Check if we're running in a test environment.

    Returns:
        bool: True if ASKAI_TESTING environment variable is set
    """
    return os.environ.get('ASKAI_TESTING', '').lower() in ('true', '1', 'yes')

def create_test_config_from_production():
    """
    Create a test configuration file by copying the production config.
    Modifies paths to use test-specific directories to avoid conflicts.

    Returns:
        bool: True if config was created successfully, False otherwise
    """
    try:
        if not os.path.exists(CONFIG_PATH):
            print(f"Error: Production config file not found at {CONFIG_PATH}")
            return False

        # Copy the production config
        shutil.copy2(CONFIG_PATH, TEST_CONFIG_PATH)

        # Load and modify the test config
        with open(TEST_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # Modify paths for testing
        if 'log_path' in config:
            config['log_path'] = "~/.askai/test/askai_test.log"

        if 'patterns' in config and 'private_patterns_path' in config['patterns']:
            if config['patterns']['private_patterns_path']:
                # Add '_test' suffix to private patterns path
                original_path = config['patterns']['private_patterns_path']
                if original_path.endswith('/'):
                    config['patterns']['private_patterns_path'] = original_path.rstrip('/') + '_test/'
                else:
                    config['patterns']['private_patterns_path'] = original_path + '_test'

        if 'chat' in config and 'storage_path' in config['chat']:
            config['chat']['storage_path'] = "~/.askai/test/chats"

        # Write the modified test config
        with open(TEST_CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

        print(f"Test configuration created at {TEST_CONFIG_PATH}")
        print("Modified settings for testing:")
        print(f"  - Log path: {config.get('log_path', 'unchanged')}")
        print(f"  - Chat storage: {config['chat']['storage_path']}")
        if config.get('patterns', {}).get('private_patterns_path'):
            print(f"  - Private patterns: {config['patterns']['private_patterns_path']}")

        return True

    except Exception as e:
        print(f"Error creating test config: {str(e)}")
        return False

def get_config_path():
    """
    Get the appropriate configuration file path based on environment.

    Returns:
        str: Path to the configuration file to use
    """
    if is_test_environment():
        if not os.path.exists(TEST_CONFIG_PATH):
            # Check if we're in a non-interactive environment (CI/automated testing)
            is_interactive = os.isatty(0)  # Check if stdin is a terminal

            if not is_interactive:
                # Non-interactive mode: try to create test config automatically
                print(f"Test configuration file not found at {TEST_CONFIG_PATH}")
                print("Creating test configuration automatically (non-interactive mode)...")
                if create_test_config_from_production():
                    return TEST_CONFIG_PATH
                else:
                    print("Failed to create test config. Using production config.")
                    return CONFIG_PATH
            else:
                # Interactive mode: ask the user
                print(f"\nTest configuration file not found at {TEST_CONFIG_PATH}")
                print("This file is needed to run tests without affecting your production configuration.")

                while True:
                    choice = input("Would you like to create it as a copy from your production config? (y/n): ").lower().strip()
                    if choice in ['y', 'yes']:
                        if create_test_config_from_production():
                            return TEST_CONFIG_PATH
                        else:
                            print("Failed to create test config. Using production config.")
                            return CONFIG_PATH
                    elif choice in ['n', 'no']:
                        print("Using production config for testing.")
                        return CONFIG_PATH
                    else:
                        print("Please enter 'y' for yes or 'n' for no.")
        else:
            return TEST_CONFIG_PATH

    return CONFIG_PATH

def load_config():
    """
    Load and parse the YAML configuration file.
    Automatically uses test configuration when in test environment.

    Returns:
        dict: The parsed configuration as a dictionary

    Raises:
        FileNotFoundError: If the configuration file doesn't exist
    """
    config_path = get_config_path()

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
