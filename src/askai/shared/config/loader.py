"""
Configuration module for AskAI CLI application.
Handles loading of user configuration from YAML files.
Supports proper ~/.askai directory structure with initialization and setup wizard.
"""

# Standard library imports
import os
import sys

# Third-party imports
import yaml

# Configuration paths
ASKAI_DIR = os.path.expanduser("~/.askai")
CONFIG_PATH = os.path.join(ASKAI_DIR, "config.yml")
CHATS_DIR = os.path.join(ASKAI_DIR, "chats")
LOGS_DIR = os.path.join(ASKAI_DIR, "logs")

# Test paths
TEST_DIR = os.path.join(ASKAI_DIR, "test")
TEST_CONFIG_PATH = os.path.join(TEST_DIR, "config.yml")
TEST_CHATS_DIR = os.path.join(TEST_DIR, "chats")
TEST_LOGS_DIR = os.path.join(TEST_DIR, "logs")

def is_test_environment():
    """
    Check if we're running in a test environment.

    Returns:
        bool: True if ASKAI_TESTING environment variable is set
    """
    return os.environ.get('ASKAI_TESTING', '').lower() in ('true', '1', 'yes')

def create_directory_structure(test_mode=False):
    """
    Create the ~/.askai directory structure.

    Args:
        test_mode: If True, create test directories as well

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create main directories
        os.makedirs(ASKAI_DIR, exist_ok=True)
        os.makedirs(CHATS_DIR, exist_ok=True)
        os.makedirs(LOGS_DIR, exist_ok=True)

        if test_mode:
            # Create test directories
            os.makedirs(TEST_DIR, exist_ok=True)
            os.makedirs(TEST_CHATS_DIR, exist_ok=True)
            os.makedirs(TEST_LOGS_DIR, exist_ok=True)

        return True
    except Exception as e:
        print(f"Error creating directory structure: {str(e)}")
        return False

def load_config_template():
    """
    Load the config template from config/config_example.yml

    Returns:
        dict: The template configuration with metadata
    """
    try:
        # Get the path to config_example.yml relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        template_path = os.path.join(project_root, "config", "config_example.yml")

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Config template not found at {template_path}")

        with open(template_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config template: {str(e)}")
        return None

def is_placeholder_value(value):
    """
    Determine if a value is a placeholder that needs user input.

    Args:
        value: The value to check

    Returns:
        bool: True if it's a placeholder, False if it's a default
    """
    if isinstance(value, str):
        # Common placeholder patterns
        placeholder_patterns = [
            "PLACEHOLDER_"
        ]

        value_lower = value.lower()
        return any(pattern in value_lower for pattern in placeholder_patterns)

    return False

def get_user_input_for_setting(key, value, path="", depth=0):
    """
    Get user input for a specific configuration setting.

    Args:
        key: The configuration key
        value: The current/default value
        path: The nested path to this setting
        depth: The nesting depth

    Returns:
        The user's input or the default value
    """
    indent = "  " * depth
    full_key = f"{path}.{key}" if path else key

    # Handle different types of values
    if isinstance(value, dict):
        print(f"{indent}[{key.upper()} SETTINGS]")
        result = {}
        for sub_key, sub_value in value.items():
            result[sub_key] = get_user_input_for_setting(sub_key, sub_value, full_key, depth + 1)
        return result

    if isinstance(value, list):
        # For lists, just return the default for now
        return value

    if value is None:
        # Handle null values
        user_input = input(f"{indent}{key}: ").strip()
        return user_input if user_input else None

    if isinstance(value, bool):
        # Handle boolean values
        while True:
            user_input = input(f"{indent}{key} (y/n, default: {'y' if value else 'n'}): ").strip().lower()
            if not user_input:
                return value
            if user_input in ['y', 'yes', 'true', '1']:
                return True
            if user_input in ['n', 'no', 'false', '0']:
                return False
            print(f"{indent}Please enter y/n")

    if isinstance(value, (int, float)):
        # Handle numeric values
        while True:
            user_input = input(f"{indent}{key} (default: {value}): ").strip()
            if not user_input:
                return value
            try:
                return type(value)(user_input)
            except ValueError:
                print(f"{indent}Please enter a valid number")

    else:
        # Handle string values
        is_required = is_placeholder_value(value)

        if is_required:
            # This is a placeholder - user must provide a value
            while True:
                user_input = input(f"{indent}{key} (required): ").strip()
                if user_input:
                    return user_input
                print(f"{indent}This setting is required. Please provide a value.")
        else:
            # This is a default value - user can accept or override
            user_input = input(f"{indent}{key} (default: '{value}'): ").strip()
            return user_input if user_input else value

def run_dynamic_setup_wizard():
    """
    Run a dynamic setup wizard based on the config template.

    Returns:
        dict: The created configuration
    """
    print("\n" + "="*60)
    print("           Welcome to AskAI Setup Wizard")
    print("="*60)
    print("\nThis wizard will help you set up your AskAI configuration.")
    print("You can change these settings later by editing ~/.askai/config.yml")
    print("\nPress Enter to accept default values, or type a new value to override.")
    print("Required fields (placeholders) must be filled in.\n")

    # Load the configuration template
    template = load_config_template()
    if not template:
        print("Error: Could not load configuration template.")
        print("Please ensure config/config_example.yml exists in the project.")
        return None

    # Update template with proper default paths for the new structure
    if 'log_path' in template:
        template['log_path'] = "~/.askai/logs/askai.log"
    if 'chat' in template and 'storage_path' in template['chat']:
        template['chat']['storage_path'] = "~/.askai/chats"
    if 'patterns' in template and 'private_patterns_path' in template['patterns']:
        if not template['patterns']['private_patterns_path']:
            template['patterns']['private_patterns_path'] = ""  # Keep empty as default

    # Ensure interface configuration exists with sensible defaults
    if 'interface' not in template:
        template['interface'] = {
            'default_mode': 'cli',
            'tui_features': {
                'enabled': True,
                'auto_fallback': True,
                'theme': 'dark',
                'animations': True,
                'preview_pane': True,
                'search_highlight': True
            }
        }

    # Process the configuration interactively
    config = {}

    # Group settings for better organization
    core_settings = ['api_key', 'default_model', 'default_vision_model', 'default_pdf_model', 'base_url']

    print("CORE SETTINGS:")
    print("-" * 15)
    for key in core_settings:
        if key in template:
            config[key] = get_user_input_for_setting(key, template[key])

    print("\nOTHER SETTINGS:")
    print("-" * 15)
    for key, value in template.items():
        if key not in core_settings:
            config[key] = get_user_input_for_setting(key, value)

    print("\n" + "="*60)
    print("           Setup Complete!")
    print("="*60)
    print(f"Configuration will be saved to: {CONFIG_PATH}")
    print("You can edit this file later to modify settings.")

    return config

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

        # Ensure test directory exists
        create_directory_structure(test_mode=True)

        # Load and modify the production config
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # Modify paths for testing
        if 'log_path' in config:
            config['log_path'] = "~/.askai/test/logs/askai_test.log"

        if 'patterns' in config and 'private_patterns_path' in config['patterns']:
            # For testing, remove private patterns path to avoid creating non-existent directories
            # Private patterns are optional, so tests can run without them
            config['patterns']['private_patterns_path'] = None

        if 'chat' in config and 'storage_path' in config['chat']:
            config['chat']['storage_path'] = "~/.askai/test/chats"

        # Write the modified test config
        with open(TEST_CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

        print(f"Test configuration created at {TEST_CONFIG_PATH}")
        print("Modified settings for testing:")
        print(f"  - Log path: {config.get('log_path', 'unchanged')}")
        print(f"  - Chat storage: {config['chat']['storage_path']}")
        print("  - Private patterns: disabled for testing")

        return True

    except Exception as e:
        print(f"Error creating test config: {str(e)}")
        return False

def ensure_askai_setup():
    """
    Ensure that AskAI is properly set up. Run setup wizard if needed.

    Returns:
        bool: True if setup is complete, False if user chose to exit
    """
    # Safety check: In test environment, always return True immediately
    if is_test_environment():
        return True

    # Check if main directory structure exists
    if not os.path.exists(ASKAI_DIR):
        print("\n" + "="*60)
        print("           AskAI First Time Setup")
        print("="*60)
        print(f"\nAskAI needs to create its directory structure at: {ASKAI_DIR}")
        print("This will include directories for configuration, chats, and logs.")

        while True:
            choice = input("\nWould you like to create the AskAI directory structure? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                if not create_directory_structure():
                    print("Failed to create directory structure.")
                    return False
                break
            if choice in ['n', 'no']:
                print("AskAI requires the directory structure to function. Exiting.")
                return False
            print("Please enter 'y' for yes or 'n' for no.")

    # Check if configuration file exists
    config_path = TEST_CONFIG_PATH if is_test_environment() else CONFIG_PATH

    if not os.path.exists(config_path):
        if is_test_environment():
            # In test mode, try to create from production config
            if os.path.exists(CONFIG_PATH):
                # In test mode, always be non-interactive
                print("Test configuration not found. Creating automatically from production config...")
                create_directory_structure(test_mode=True)
                return create_test_config_from_production()
            print("Production configuration not found. Please run setup in production mode first.")
            return False
        # Production mode - run setup wizard
        config = run_dynamic_setup_wizard()

        if not config:
            print("Setup wizard failed. Cannot continue without configuration.")
            return False

        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
            print("Configuration saved successfully!")
            return True
        except Exception as e:
            print(f"Error saving configuration: {str(e)}")
            return False

    return True

def get_config_path():
    """
    Get the appropriate configuration file path based on environment.

    Returns:
        str: Path to the configuration file to use
    """
    if is_test_environment():
        return TEST_CONFIG_PATH
    return CONFIG_PATH

def load_config():
    """
    Load and parse the YAML configuration file.
    Automatically ensures setup is complete and uses appropriate config for environment.

    Returns:
        dict: The parsed configuration as a dictionary

    Raises:
        SystemExit: If setup is incomplete or configuration cannot be loaded
    """
    # In test environment, try to load test configuration or fall back to production config
    if is_test_environment():
        # First, try to load test configuration if it exists
        if os.path.exists(TEST_CONFIG_PATH):
            try:
                with open(TEST_CONFIG_PATH, "r", encoding="utf-8") as f:
                    test_config = yaml.safe_load(f)
                    # Ensure test config has valid base_url and api_key
                    if (test_config.get('base_url') == 'https://test.api.com' or
                        test_config.get('api_key') == 'test-key'):
                        # This is a dummy config, try to fall back to production
                        pass
                    else:
                        return test_config
            except Exception as e:
                print(f"Warning: Could not load test config: {e}")

        # If test config doesn't exist or has dummy values, check for production config
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    prod_config = yaml.safe_load(f)
                    # Use production config but modify paths for testing
                    prod_config['enable_logging'] = False
                    prod_config['log_path'] = '/tmp/test.log'
                    prod_config['log_level'] = 'ERROR'
                    if 'chat' in prod_config:
                        prod_config['chat']['storage_path'] = '/tmp/test-chats'
                    if 'interface' in prod_config and 'tui_features' in prod_config['interface']:
                        prod_config['interface']['tui_features']['enabled'] = False
                        prod_config['interface']['tui_features']['animations'] = False
                    return prod_config
            except Exception as e:
                print(f"Warning: Could not load production config for testing: {e}")

        # Last resort: return minimal config with warnings
        print("Warning: Using minimal test configuration. Integration tests may fail.")
        return {
            'api_key': 'test-key',
            'default_model': 'test-model',
            'base_url': 'https://test.api.com',
            'enable_logging': False,
            'log_path': '/tmp/test.log',
            'log_level': 'ERROR',
            'patterns': {
                'private_patterns_path': ''
            },
            'web_search': {
                'enabled': False,
                'method': 'plugin',
                'max_results': 5
            },
            'chat': {
                'storage_path': '/tmp/test-chats',
                'max_history': 10
            },
            'interface': {
                'default_mode': 'cli',
                'tui_features': {
                    'enabled': False,
                    'auto_fallback': True,
                    'theme': 'dark',
                    'animations': False
                }
            }
        }

    # Ensure AskAI is properly set up
    if not ensure_askai_setup():
        sys.exit(1)

    config_path = get_config_path()

    if not os.path.exists(config_path):
        print(f"Configuration file not found at {config_path}")
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        sys.exit(1)


def get_interface_mode(config=None):
    """
    Get the configured default interface mode.

    Args:
        config (dict, optional): Configuration dict. If None, loads from file.

    Returns:
        str: 'cli' or 'tui' based on configuration
    """
    if config is None:
        config = load_config()

    return config.get('interface', {}).get('default_mode', 'cli')


def get_tui_features(config=None):
    """
    Get TUI feature configuration.

    Args:
        config (dict, optional): Configuration dict. If None, loads from file.

    Returns:
        dict: TUI features configuration with defaults
    """
    if config is None:
        config = load_config()

    defaults = {
        'enabled': True,
        'auto_fallback': True,
        'theme': 'dark',
        'animations': True,
        'preview_pane': True,
        'search_highlight': True
    }

    tui_config = config.get('interface', {}).get('tui_features', {})

    # Merge defaults with user configuration
    result = defaults.copy()
    result.update(tui_config)

    return result


def is_tui_enabled(config=None):
    """
    Check if TUI functionality is enabled in configuration.

    Args:
        config (dict, optional): Configuration dict. If None, loads from file.

    Returns:
        bool: True if TUI is enabled
    """
    tui_features = get_tui_features(config)
    return tui_features.get('enabled', True)


def should_auto_fallback_to_cli(config=None):
    """
    Check if auto-fallback to CLI is enabled when TUI fails.

    Args:
        config (dict, optional): Configuration dict. If None, loads from file.

    Returns:
        bool: True if auto-fallback is enabled
    """
    tui_features = get_tui_features(config)
    return tui_features.get('auto_fallback', True)
