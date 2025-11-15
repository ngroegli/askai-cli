"""
Configuration management for the AskAI CLI application.
"""

# Import main functions for backward compatibility
from .loader import (
    load_config, ensure_askai_setup, get_config_path,
    ASKAI_DIR, CONFIG_PATH, CHATS_DIR, LOGS_DIR, TEST_DIR,
    TEST_CHATS_DIR, TEST_CONFIG_PATH, TEST_LOGS_DIR,
    is_test_environment, create_test_config_from_production
)

__all__ = [
    'load_config', 'ensure_askai_setup', 'get_config_path',
    'ASKAI_DIR', 'CONFIG_PATH', 'CHATS_DIR', 'LOGS_DIR', 'TEST_DIR',
    'TEST_CHATS_DIR', 'TEST_CONFIG_PATH', 'TEST_LOGS_DIR',
    'is_test_environment', 'create_test_config_from_production'
]
