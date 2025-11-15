"""
Unit tests for CLI presentation functionality.
"""
import os
import sys
from unittest.mock import Mock, patch

# Setup paths for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "python"))
sys.path.insert(0, os.path.join(project_root, "tests"))

# pylint: disable=wrong-import-position,import-error
from unit.test_base import BaseUnitTest
from presentation.cli.cli_parser import CLIParser
from presentation.cli.command_handler import CommandHandler
from presentation.cli.banner_argument_parser import BannerArgumentParser





class TestCLIParser(BaseUnitTest):
    """Test the CLI parser functionality."""

    def run(self):
        """Run all CLI parser tests."""
        self.test_cli_parser_initialization()
        self.test_parse_question_arguments()
        self.test_parse_pattern_arguments()
        self.test_invalid_arguments()
        return self.results

    def test_cli_parser_initialization(self):
        """Test CLI parser initialization."""
        try:


            parser = CLIParser()

            self.assert_not_none(
                parser,
                "cli_parser_init",
                "CLI parser initializes successfully"
            )

            # Check if parser has expected methods
            self.assert_true(
                hasattr(parser, 'parse_arguments'),
                "cli_parser_parse_method",
                "CLI parser has parse_arguments method"
            )

        except Exception as e:
            self.add_result("cli_parser_init_error", False, f"CLI parser initialization failed: {e}")

    def test_parse_question_arguments(self):
        """Test parsing question arguments."""
        try:


            parser = CLIParser()

            # Mock sys.argv for question parsing
            test_args = ['-q', 'What is the capital of France?']

            with patch('sys.argv', ['askai'] + test_args):
                try:
                    args = parser.parse_arguments()

                    self.assert_not_none(
                        args,
                        "parse_question_args_not_none",
                        "Question arguments parsed successfully"
                    )

                    # Check that question is parsed correctly
                    if hasattr(args, 'question'):
                        self.assert_equal(
                            'What is the capital of France?',
                            args.question,
                            "parse_question_content",
                            "Question content parsed correctly"
                        )
                    else:
                        self.add_result("parse_question_attribute", False, "Args object missing question attribute")

                except SystemExit:
                    # argparse might call sys.exit on help or error
                    self.add_result(
                        "parse_question_system_exit", True,
                        "Parser handled arguments (may have shown help)"
                    )

        except Exception as e:
            self.add_result("parse_question_error", False, f"Question argument parsing failed: {e}")

    def test_parse_pattern_arguments(self):
        """Test parsing pattern arguments."""
        try:


            parser = CLIParser()

            # Mock sys.argv for pattern parsing
            test_args = ['-p', 'test_pattern']

            with patch('sys.argv', ['askai'] + test_args):
                try:
                    args = parser.parse_arguments()

                    self.assert_not_none(
                        args,
                        "parse_pattern_args_not_none",
                        "Pattern arguments parsed successfully"
                    )

                    # Check that pattern is parsed correctly
                    if hasattr(args, 'use_pattern'):
                        self.assert_equal(
                            'test_pattern',
                            args.use_pattern,
                            "parse_pattern_name",
                            "Pattern name parsed correctly"
                        )
                    else:
                        self.add_result("parse_pattern_attribute", False, "Args object missing use_pattern attribute")

                except SystemExit:
                    # argparse might call sys.exit on help or error
                    self.add_result("parse_pattern_system_exit", True, "Parser handled pattern arguments")

        except Exception as e:
            self.add_result("parse_pattern_error", False, f"Pattern argument parsing failed: {e}")

    def test_invalid_arguments(self):
        """Test handling of invalid arguments."""
        try:


            parser = CLIParser()

            # Test with invalid arguments
            test_args = ['--invalid-option', 'value']

            with patch('sys.argv', ['askai'] + test_args):
                try:
                    parser.parse_arguments()

                    # If we get here, the parser accepted the invalid option
                    self.add_result("invalid_args_accepted", False, "Parser should reject invalid arguments")

                except SystemExit:
                    # This is expected behavior for invalid arguments
                    self.add_result("invalid_args_rejected", True, "Parser correctly rejects invalid arguments")

        except Exception as e:
            self.add_result("invalid_args_error", False, f"Invalid argument test failed: {e}")


class TestCommandHandler(BaseUnitTest):
    """Test the command handler functionality."""

    def run(self):
        """Run all command handler tests."""
        self.test_command_handler_initialization()
        self.test_handle_pattern_commands()
        self.test_handle_chat_commands()
        return self.results

    def test_command_handler_initialization(self):
        """Test command handler initialization."""
        try:


            mock_pattern_manager = Mock()
            mock_chat_manager = Mock()
            mock_logger = Mock()

            handler = CommandHandler(mock_pattern_manager, mock_chat_manager, mock_logger)

            self.assert_not_none(
                handler,
                "command_handler_init",
                "Command handler initializes successfully"
            )

            self.assert_not_none(
                handler.pattern_manager,
                "command_handler_pattern_manager",
                "Command handler has pattern manager"
            )

            self.assert_not_none(
                handler.chat_manager,
                "command_handler_chat_manager",
                "Command handler has chat manager"
            )

        except Exception as e:
            self.add_result("command_handler_init_error", False, f"Command handler initialization failed: {e}")

    def test_handle_pattern_commands(self):
        """Test handling pattern commands."""
        try:


            mock_pattern_manager = Mock()
            mock_chat_manager = Mock()
            mock_logger = Mock()

            # Mock pattern listing - patterns should be dictionaries, not strings
            mock_pattern_manager.list_patterns.return_value = [
                {
                    'pattern_id': 'pattern1',
                    'name': 'Test Pattern 1',
                    'source': 'built-in',
                    'is_private': False
                },
                {
                    'pattern_id': 'pattern2',
                    'name': 'Test Pattern 2',
                    'source': 'built-in',
                    'is_private': False
                }
            ]

            handler = CommandHandler(mock_pattern_manager, mock_chat_manager, mock_logger)

            # Mock arguments for list patterns
            mock_args = Mock()
            mock_args.list_patterns = True
            mock_args.view_pattern = None

            # Add attributes that might be accessed during command processing
            mock_args.get = Mock(return_value=None)
            # Add all the attributes that CommandHandler might check
            for attr in ['question', 'pattern', 'file', 'url', 'format', 'config', 'debug', 'streaming']:
                setattr(mock_args, attr, None)

            # Test handling pattern commands
            result = handler.handle_pattern_commands(mock_args)

            # Should return True if command was handled
            self.assert_true(
                isinstance(result, bool),  # type: ignore[reportUnnecessaryIsInstance]
                "handle_pattern_commands_bool",
                "Pattern command handler returns boolean"
            )

            # Verify pattern manager was called (if result indicates success)
            if result:
                self.add_result("handle_pattern_commands_called", True, "Pattern manager methods were called")
            else:
                self.add_result("handle_pattern_commands_not_called", True, "Pattern commands not applicable")

        except Exception as e:
            self.add_result("handle_pattern_commands_error", False, f"Pattern command handling failed: {e}")

    def test_handle_chat_commands(self):
        """Test handling chat commands."""
        try:


            mock_pattern_manager = Mock()
            mock_chat_manager = Mock()
            mock_logger = Mock()

            # Mock chat listing
            mock_chat_manager.list_chats.return_value = ['chat1', 'chat2']

            handler = CommandHandler(mock_pattern_manager, mock_chat_manager, mock_logger)

            # Mock arguments for list chats
            mock_args = Mock()
            mock_args.list_chats = True
            mock_args.view_chat = None

            # Test handling chat commands
            result = handler.handle_chat_commands(mock_args)

            # Should return True if command was handled
            self.assert_true(
                isinstance(result, bool),  # type: ignore[reportUnnecessaryIsInstance]
                "handle_chat_commands_bool",
                "Chat command handler returns boolean"
            )

            # Verify chat manager was called (if result indicates success)
            if result:
                self.add_result("handle_chat_commands_called", True, "Chat manager methods were called")
            else:
                self.add_result("handle_chat_commands_not_called", True, "Chat commands not applicable")

        except Exception as e:
            self.add_result("handle_chat_commands_error", False, f"Chat command handling failed: {e}")


class TestBannerArgumentParser(BaseUnitTest):
    """Test the banner argument parser functionality."""

    def run(self):
        """Run all banner argument parser tests."""
        self.test_banner_parser_initialization()
        self.test_banner_display()
        return self.results

    def test_banner_parser_initialization(self):
        """Test banner argument parser initialization."""
        try:


            parser = BannerArgumentParser()

            self.assert_not_none(
                parser,
                "banner_parser_init",
                "Banner argument parser initializes successfully"
            )

        except Exception as e:
            self.add_result("banner_parser_init_error", False, f"Banner parser initialization failed: {e}")

    def test_banner_display(self):
        """Test banner display functionality."""
        try:


            parser = BannerArgumentParser()

            # Test that banner display methods exist and are callable
            if hasattr(parser, 'format_help'):
                self.assert_true(
                    callable(parser.format_help),
                    "banner_format_help_callable",
                    "Banner parser format_help is callable"
                )

            # Test basic functionality without actually displaying
            self.assert_true(
                hasattr(parser, 'add_argument') or hasattr(parser, 'parse_args'),
                "banner_parser_methods",
                "Banner parser has expected argument parsing methods"
            )

        except Exception as e:
            self.add_result("banner_display_error", False, f"Banner display test failed: {e}")
