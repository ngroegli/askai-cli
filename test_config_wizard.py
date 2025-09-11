#!/usr/bin/env python3
"""
Test script for the dynamic configuration wizard.
This allows testing the wizard without affecting production config.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from python.config import load_config_template, run_dynamic_setup_wizard

def test_template_loading():
    """Test loading the configuration template."""
    print("Testing configuration template loading...")
    template = load_config_template()

    if template:
        print("✓ Template loaded successfully!")
        print("\nTemplate structure:")
        def print_dict(d, indent=0):
            for key, value in d.items():
                spaces = "  " * indent
                if isinstance(value, dict):
                    print(f"{spaces}{key}:")
                    print_dict(value, indent + 1)
                else:
                    print(f"{spaces}{key}: {value}")

        print_dict(template)
    else:
        print("✗ Failed to load template")

def test_placeholder_detection():
    """Test placeholder detection logic."""
    from python.config import is_placeholder_value

    print("\nTesting placeholder detection...")

    test_cases = [
        ("your_openrouter_api_key", True),
        ("openai/gpt-4o", False),
        ("true", False),
        ("5", False),
        ("replace_this_value", True),
        ("enter_your_key", True),
        ("https://openrouter.ai/api/v1/", False),
        ("INFO", False)
    ]

    for value, expected in test_cases:
        result = is_placeholder_value(value)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{value}' -> {result} (expected: {expected})")

if __name__ == "__main__":
    test_template_loading()
    test_placeholder_detection()

    print("\n" + "="*50)
    print("To test the full wizard (simulation mode):")
    print("python test_config_wizard.py --wizard")

    if "--wizard" in sys.argv:
        print("\nRunning wizard in simulation mode...")
        print("(Note: This won't save any actual configuration)")
        config = run_dynamic_setup_wizard()
        print("\nGenerated configuration:")
        import yaml
        print(yaml.dump(config, default_flow_style=False))
