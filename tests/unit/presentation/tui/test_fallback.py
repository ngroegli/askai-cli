"""
Unit tests for TUI fallback utilities.
"""

import os
import unittest
from unittest.mock import patch

# Import the module under test
from askai.presentation.tui.utils.fallback import (
    check_tui_environment,
    explain_tui_unavailable,
    smart_fallback_message,
    configure_tui_environment
)


class TestTUIFallback(unittest.TestCase):
    """Test TUI fallback functionality."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        # Clean environment for consistent testing
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up after tests."""
        super().tearDown()
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch('python.presentation.tui.utils.fallback.os.isatty')
    def test_check_tui_environment_no_textual(self, mock_isatty):
        """Test environment check when textual is not available."""
        mock_isatty.return_value = True

        with patch.dict('sys.modules', {'textual': None}):
            # This will cause import to fail
            result = check_tui_environment()

        self.assertFalse(result['textual_available'])
        self.assertTrue(result['terminal_compatible'])
        self.assertTrue(result['user_preference'])
        self.assertFalse(result['overall_compatible'])
        self.assertIn("Textual library not installed", str(result['issues']))

    @patch('python.presentation.tui.utils.fallback.os.isatty')
    def test_check_tui_environment_no_terminal(self, mock_isatty):
        """Test environment check when not in terminal."""
        mock_isatty.return_value = False

        result = check_tui_environment()

        self.assertFalse(result['terminal_compatible'])
        self.assertFalse(result['overall_compatible'])
        self.assertIn("Not running in an interactive terminal", str(result['issues']))

    @patch('python.presentation.tui.utils.fallback.os.isatty')
    def test_check_tui_environment_disabled_by_env(self, mock_isatty):
        """Test environment check when TUI is disabled via environment variable."""
        mock_isatty.return_value = True
        os.environ['ASKAI_NO_TUI'] = '1'

        result = check_tui_environment()

        self.assertFalse(result['user_preference'])
        self.assertFalse(result['overall_compatible'])
        self.assertIn("TUI disabled via ASKAI_NO_TUI", str(result['issues']))

    @patch('python.presentation.tui.utils.fallback.os.isatty')
    def test_check_tui_environment_dumb_terminal(self, mock_isatty):
        """Test environment check with dumb terminal."""
        mock_isatty.return_value = True
        os.environ['TERM'] = 'dumb'

        result = check_tui_environment()

        self.assertFalse(result['terminal_compatible'])
        self.assertFalse(result['overall_compatible'])
        self.assertIn("Terminal type 'dumb' not supported", str(result['issues']))

    def test_explain_tui_unavailable_compatible(self):
        """Test explanation when TUI is compatible."""
        env_check = {
            'overall_compatible': True,
            'issues': []
        }

        explanation = explain_tui_unavailable(env_check)
        self.assertEqual(explanation, "TUI is available and compatible.")

    def test_explain_tui_unavailable_with_issues(self):
        """Test explanation when TUI has issues."""
        env_check = {
            'overall_compatible': False,
            'textual_available': False,
            'issues': ["Textual library not installed", "Not in terminal"]
        }

        explanation = explain_tui_unavailable(env_check)
        self.assertIn("TUI interface unavailable:", explanation)
        self.assertIn("Textual library not installed", explanation)
        self.assertIn("Not in terminal", explanation)
        self.assertIn("pip install textual>=0.40.0", explanation)

    def test_smart_fallback_message_compatible(self):
        """Test smart fallback message when compatible."""
        env_check = {'overall_compatible': True}

        message = smart_fallback_message("pattern selection", env_check)
        self.assertIn("Using TUI for pattern selection", message)

    def test_smart_fallback_message_no_textual(self):
        """Test smart fallback message when textual unavailable."""
        env_check = {
            'overall_compatible': False,
            'textual_available': False,
            'terminal_compatible': True
        }

        message = smart_fallback_message("chat management", env_check)
        self.assertIn("TUI not available for chat management", message)
        self.assertIn("simple interface", message)

    def test_smart_fallback_message_no_terminal(self):
        """Test smart fallback message when terminal incompatible."""
        env_check = {
            'overall_compatible': False,
            'textual_available': True,
            'terminal_compatible': False
        }

        message = smart_fallback_message("model selection", env_check)
        self.assertIn("Terminal not compatible", message)
        self.assertIn("simple interface", message)

    def test_configure_tui_environment_recommendations(self):
        """Test TUI environment configuration recommendations."""
        with patch('python.presentation.tui.utils.fallback.check_tui_environment') as mock_check:
            mock_check.return_value = {
                'overall_compatible': False,
                'textual_available': False,
                'issues': [
                    "Textual library not installed (pip install textual)",
                    "TUI disabled via ASKAI_NO_TUI environment variable"
                ]
            }

            result = configure_tui_environment()

            self.assertFalse(result['configured'])
            self.assertEqual(len(result['recommendations']), 2)

            # Check for install recommendation
            install_rec = next(
                (r for r in result['recommendations'] if r['action'] == 'install_textual'),
                None
            )
            self.assertIsNotNone(install_rec)
            if install_rec is not None:
                self.assertIn("pip install textual", install_rec['command'])

            # Check for enable TUI recommendation
            enable_rec = next(
                (r for r in result['recommendations'] if r['action'] == 'enable_tui'),
                None
            )
            self.assertIsNotNone(enable_rec)
            if enable_rec is not None:
                self.assertIn("unset ASKAI_NO_TUI", enable_rec['command'])

    def test_configure_tui_environment_already_configured(self):
        """Test TUI environment when already properly configured."""
        with patch('python.presentation.tui.utils.fallback.check_tui_environment') as mock_check:
            mock_check.return_value = {
                'overall_compatible': True,
                'textual_available': True,
                'issues': []
            }

            result = configure_tui_environment()

            self.assertTrue(result['configured'])
            self.assertEqual(len(result['recommendations']), 0)
            self.assertIn('ASKAI_TUI_THEME', result['environment_vars'])


if __name__ == '__main__':
    unittest.main()
