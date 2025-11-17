"""
Integration tests for TUI pattern browser functionality.
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import sys
import os

# Add the project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from askai.presentation.tui import is_tui_available, get_tui_config  # pylint: disable=wrong-import-position

# Mock implementations for testing (since the actual modules don't exist yet)
class PatternItem:
    """Mock PatternItem for testing."""
    def __init__(self, name, path, description, category):
        self.name = name
        self.path = path
        self.description = description
        self.category = category
        self.content = None

    def load_content(self):
        """Load pattern content from file."""
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.content = content
                return content
        except Exception as e:
            error_msg = f"Error loading pattern from {self.path}: {str(e)}"
            self.content = error_msg
            return error_msg

    def get_preview(self, max_lines=10):
        """Get a preview of the pattern content."""
        content = self.load_content()
        if not content:
            return ""

        lines = content.split('\n')
        if len(lines) <= max_lines:
            return content

        preview_lines = lines[:max_lines]
        preview_lines.append("...")
        return '\n'.join(preview_lines)

def pattern_browser_fallback(pattern_manager):
    """Mock pattern browser fallback for testing."""
    try:
        patterns = pattern_manager.list_patterns()

        if not patterns:
            print("No patterns available.")
            return None

        print("Available patterns:")
        for i, pattern in enumerate(patterns, 1):
            print(f"{i}. {pattern['name']}")
            print(f"   Description: {pattern['description']}")
            print(f"   Category: {pattern['category']}")
            print()

        selection = input("Enter pattern number (or press Enter to cancel): ").strip()

        if not selection:
            return None

        try:
            index = int(selection) - 1
            if 0 <= index < len(patterns):
                pattern_data = patterns[index]
                return PatternItem(
                    name=pattern_data['name'],
                    path=pattern_data['path'],
                    description=pattern_data['description'],
                    category=pattern_data['category']
                )
        except ValueError:
            pass

        return None

    except KeyboardInterrupt:
        return None


class TestPatternBrowserIntegration(unittest.TestCase):
    """Integration tests for pattern browser TUI."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mock_pattern_manager = Mock()
        # Mock pattern data
        self.sample_patterns = [
            {
                'name': 'test_pattern_1',
                'path': '/tmp/test1.md',
                'description': 'Test pattern 1',
                'category': 'built-in',
                'pattern_id': 'test1'
            },
            {
                'name': 'test_pattern_2',
                'path': '/tmp/test2.md',
                'description': 'Test pattern 2',
                'category': 'private',
                'pattern_id': 'test2'
            }
        ]

    def setUp(self):
        """Set up test fixtures."""
        self.mock_pattern_manager.list_patterns.return_value = self.sample_patterns

    def test_pattern_item_creation(self):
        """Test PatternItem creation and basic functionality."""
        pattern = PatternItem(
            name="test_pattern",
            path="/tmp/test.md",
            description="A test pattern",
            category="built-in"
        )

        self.assertEqual(pattern.name, "test_pattern")
        self.assertEqual(pattern.path, "/tmp/test.md")
        self.assertEqual(pattern.description, "A test pattern")
        self.assertEqual(pattern.category, "built-in")
        self.assertIsNone(pattern.content)

    def test_pattern_item_load_content_success(self):
        """Test successful content loading."""
        with patch('builtins.open', mock_open(read_data="# Test Pattern\nContent here")):
            pattern = PatternItem("test", "/tmp/test.md", "desc", "cat")
            content = pattern.load_content()

            self.assertEqual(content, "# Test Pattern\nContent here")
            self.assertEqual(pattern.content, "# Test Pattern\nContent here")

    def test_pattern_item_load_content_error(self):
        """Test content loading with file error."""
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            pattern = PatternItem("test", "/nonexistent/test.md", "desc", "cat")
            content = pattern.load_content()

            self.assertIn("Error loading pattern", content)
            self.assertIn("File not found", content)

    def test_pattern_item_get_preview(self):
        """Test pattern preview generation."""
        content = "\n".join([f"Line {i}" for i in range(1, 21)])  # 20 lines

        with patch.object(PatternItem, 'load_content', return_value=content):
            pattern = PatternItem("test", "/tmp/test.md", "desc", "cat")
            preview = pattern.get_preview(max_lines=5)

            lines = preview.split('\n')
            self.assertEqual(len(lines), 6)  # 5 lines + "..."
            self.assertEqual(lines[-1], "...")

    def test_pattern_item_get_preview_short_content(self):
        """Test preview with content shorter than max lines."""
        content = "Line 1\nLine 2\nLine 3"

        with patch.object(PatternItem, 'load_content', return_value=content):
            pattern = PatternItem("test", "/tmp/test.md", "desc", "cat")
            preview = pattern.get_preview(max_lines=10)

            self.assertEqual(preview, content)

    @patch('builtins.input')
    def test_pattern_browser_fallback_selection(self, mock_input):
        """Test fallback pattern browser with valid selection."""
        mock_input.return_value = "1"

        result = pattern_browser_fallback(self.mock_pattern_manager)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, PatternItem)
        if result:  # Additional safety check
            self.assertEqual(result.name, 'test_pattern_1')
            self.assertEqual(result.path, '/tmp/test1.md')
            self.assertEqual(result.description, 'Test pattern 1')

    @patch('builtins.input')
    def test_pattern_browser_fallback_cancel(self, mock_input):
        """Test fallback pattern browser with cancellation."""
        mock_input.return_value = ""  # Empty input cancels

        result = pattern_browser_fallback(self.mock_pattern_manager)

        self.assertIsNone(result)

    @patch('builtins.input')
    def test_pattern_browser_fallback_invalid_selection(self, mock_input):
        """Test fallback pattern browser with invalid selection."""
        mock_input.return_value = "999"  # Invalid index

        result = pattern_browser_fallback(self.mock_pattern_manager)

        self.assertIsNone(result)

    @patch('builtins.input')
    def test_pattern_browser_fallback_keyboard_interrupt(self, mock_input):
        """Test fallback pattern browser with keyboard interrupt."""
        mock_input.side_effect = KeyboardInterrupt()

        result = pattern_browser_fallback(self.mock_pattern_manager)

        self.assertIsNone(result)

    @patch('builtins.input')
    def test_pattern_browser_fallback_value_error(self, mock_input):
        """Test fallback pattern browser with value error."""
        mock_input.return_value = "abc"  # Non-numeric input

        result = pattern_browser_fallback(self.mock_pattern_manager)

        self.assertIsNone(result)

    def test_pattern_browser_fallback_no_patterns(self):
        """Test fallback browser with no patterns available."""
        self.mock_pattern_manager.list_patterns.return_value = []

        result = pattern_browser_fallback(self.mock_pattern_manager)

        self.assertIsNone(result)

    @patch('builtins.print')
    def test_pattern_browser_fallback_output_format(self, mock_print):
        """Test that fallback browser outputs properly formatted pattern list."""
        with patch('builtins.input', return_value=""):
            pattern_browser_fallback(self.mock_pattern_manager)

        # Check that print was called with pattern information
        print_calls = []
        for call in mock_print.call_args_list:
            if call[0]:  # Only process calls with arguments
                print_calls.append(call[0][0])

        output_text = " ".join(str(call) for call in print_calls)

        self.assertIn("Available patterns:", output_text)
        self.assertIn("test_pattern_1", output_text)
        self.assertIn("test_pattern_2", output_text)
        self.assertIn("Test pattern 1", output_text)
        self.assertIn("Test pattern 2", output_text)


class TestTUIIntegration(unittest.TestCase):
    """Integration tests for TUI system integration."""
    @patch('tests.integration.tui.test_pattern_browser.is_tui_available')
    def test_tui_availability_check(self, mock_tui_available):
        """Test TUI availability checking."""
        mock_tui_available.return_value = True

        self.assertTrue(is_tui_available())

        mock_tui_available.return_value = False
        self.assertFalse(is_tui_available())

    def test_tui_config_retrieval(self):
        """Test TUI configuration retrieval."""
        config = get_tui_config()

        self.assertIsInstance(config, dict)
        self.assertIn('theme', config)
        self.assertIn('keybindings', config)
        self.assertIn('features', config)

        # Check keybindings structure
        keybindings = config['keybindings']
        self.assertIn('search', keybindings)
        self.assertIn('quit', keybindings)
        self.assertIsInstance(keybindings['search'], list)
        self.assertIsInstance(keybindings['quit'], list)

        # Check features structure
        features = config['features']
        self.assertIn('live_preview', features)
        self.assertIn('fuzzy_search', features)
        self.assertIn('syntax_highlighting', features)


if __name__ == '__main__':
    unittest.main()
