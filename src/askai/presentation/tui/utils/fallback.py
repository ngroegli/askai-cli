"""
TUI fallback utilities for graceful degradation when Textual is unavailable.
"""

import importlib.util
import os
import sys
from typing import Optional

# Check textual availability using importlib instead of direct import
TEXTUAL_AVAILABLE = importlib.util.find_spec("textual") is not None


def check_tui_environment() -> dict:
    """
    Check the current environment for TUI compatibility.

    Returns:
        dict: Environment check results with details
    """
    result = {
        'textual_available': False,
        'terminal_compatible': False,
        'user_preference': True,
        'overall_compatible': False,
        'issues': []
    }

    # Check if textual is available
    result['textual_available'] = TEXTUAL_AVAILABLE
    if not TEXTUAL_AVAILABLE:
        result['issues'].append("Textual library not installed (pip install textual)")

    # Check terminal compatibility
    if not os.isatty(sys.stdout.fileno()):
        result['issues'].append("Not running in an interactive terminal")
    else:
        result['terminal_compatible'] = True

    # Check environment variable override
    if os.environ.get('ASKAI_NO_TUI', '').lower() in ['1', 'true']:
        result['user_preference'] = False
        result['issues'].append("TUI disabled via ASKAI_NO_TUI environment variable")

    # Check terminal type
    term = os.environ.get('TERM', '')
    if term in ['dumb', '']:
        result['terminal_compatible'] = False
        result['issues'].append(f"Terminal type '{term}' not supported")

    # Check overall compatibility
    result['overall_compatible'] = (
        result['textual_available'] and
        result['terminal_compatible'] and
        result['user_preference']
    )

    return result


def explain_tui_unavailable(environment_check: dict) -> str:
    """
    Generate a user-friendly explanation of why TUI is unavailable.

    Args:
        environment_check: Result from check_tui_environment()

    Returns:
        str: Human-readable explanation
    """
    if environment_check['overall_compatible']:
        return "TUI is available and compatible."

    explanation = "TUI interface unavailable:"
    for issue in environment_check['issues']:
        explanation += f"\n  • {issue}"

    if not environment_check['textual_available']:
        explanation += "\n\nTo enable TUI features, install textual:"
        explanation += "\n  pip install textual>=0.40.0"

    explanation += "\n\nFalling back to traditional CLI interface."
    return explanation


def smart_fallback_message(operation: str, environment_check: Optional[dict] = None) -> str:
    """
    Generate context-specific fallback message.

    Args:
        operation: The operation being attempted (e.g., "pattern selection", "chat management")
        environment_check: Optional environment check results

    Returns:
        str: Context-specific message
    """
    if environment_check is None:
        environment_check = check_tui_environment()

    if environment_check['overall_compatible']:
        return f"Using TUI for {operation}..."

    # Brief message for fallback
    if not environment_check['textual_available']:
        return f"TUI not available for {operation}, using simple interface..."
    elif not environment_check['terminal_compatible']:
        return f"Terminal not compatible with TUI, using simple interface for {operation}..."
    else:
        return f"TUI disabled, using simple interface for {operation}..."


def configure_tui_environment() -> dict:
    """
    Attempt to configure the environment for optimal TUI experience.

    Returns:
        dict: Configuration results and recommendations
    """
    result = {
        'configured': False,
        'recommendations': [],
        'environment_vars': {}
    }

    # Check current environment
    env_check = check_tui_environment()

    # Provide recommendations based on issues
    for issue in env_check['issues']:
        if "Textual library not installed" in issue:
            result['recommendations'].append({
                'action': 'install_textual',
                'command': 'pip install textual>=0.40.0',
                'description': 'Install Textual library for TUI support'
            })

        elif "Not running in an interactive terminal" in issue:
            result['recommendations'].append({
                'action': 'use_interactive_terminal',
                'command': None,
                'description': 'Run askai in an interactive terminal (not in scripts or pipes)'
            })

        elif "TUI disabled via" in issue:
            result['recommendations'].append({
                'action': 'enable_tui',
                'command': 'unset ASKAI_NO_TUI',
                'description': 'Remove environment variable that disables TUI'
            })

        elif "Terminal type" in issue:
            result['recommendations'].append({
                'action': 'set_terminal_type',
                'command': 'export TERM=xterm-256color',
                'description': 'Set a compatible terminal type'
            })

    # Suggest optimal environment variables
    if env_check['textual_available']:
        result['environment_vars']['ASKAI_TUI_THEME'] = 'dark'  # or 'light'
        result['environment_vars']['TERM'] = os.environ.get('TERM', 'xterm-256color')

    result['configured'] = env_check['overall_compatible']
    return result


def print_tui_setup_help():
    """Print comprehensive TUI setup help."""
    print("\n=== AskAI TUI Setup Guide ===")

    config = configure_tui_environment()
    env_check = check_tui_environment()

    if env_check['overall_compatible']:
        print("✓ TUI is ready to use!")
        print("\nAvailable TUI features:")
        print("  • Interactive pattern browser with search and preview")
        print("  • Chat management with filtering and sorting")
        print("  • Modern keyboard navigation and shortcuts")

        print("\nUsage:")
        print("  askai --interactive")
        print("  askai -i")

        print("\nCustomization:")
        print("  export ASKAI_TUI_THEME=dark    # or 'light'")
        print("  export ASKAI_NO_TUI=1          # disable TUI")

    else:
        print("⚠ TUI is not available in your current environment.")
        print("\nIssues found:")
        for issue in env_check['issues']:
            print(f"  ✗ {issue}")

        print("\nRecommended actions:")
        for rec in config['recommendations']:
            print(f"  • {rec['description']}")
            if rec['command']:
                print(f"    Command: {rec['command']}")

    print("\n" + "=" * 40)


__all__ = [
    'check_tui_environment',
    'explain_tui_unavailable',
    'smart_fallback_message',
    'configure_tui_environment',
    'print_tui_setup_help'
]
