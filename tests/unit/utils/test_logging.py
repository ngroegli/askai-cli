"""
Unit tests for logging module.
"""
import os
import sys
import tempfile
import logging

# Setup paths for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, os.path.join(project_root, "tests"))

# pylint: disable=wrong-import-position,import-error
from unit.test_base import BaseUnitTest
from askai.utils.logging import (
    setup_logger,
    get_logger,
    get_log_level,
    create_log_directory,
    LOGGER_NAME
)


class TestLogging(BaseUnitTest):
    """Test the logging functionality."""

    def run(self):
        """Run all logging tests."""
        self.test_get_log_level()
        self.test_create_log_directory()
        self.test_setup_logger()
        self.test_setup_logger_debug_mode()
        self.test_setup_logger_disabled()
        self.test_get_logger()
        return self.results

    def test_get_log_level(self):
        """Test log level conversion."""
        try:
            level = get_log_level('DEBUG')
            self.assert_equal(
                level,
                logging.DEBUG,
                "log_level_debug",
                "DEBUG level converts correctly"
            )

            level = get_log_level('INFO')
            self.assert_equal(
                level,
                logging.INFO,
                "log_level_info",
                "INFO level converts correctly"
            )

            level = get_log_level('WARNING')
            self.assert_equal(
                level,
                logging.WARNING,
                "log_level_warning",
                "WARNING level converts correctly"
            )

            level = get_log_level('ERROR')
            self.assert_equal(
                level,
                logging.ERROR,
                "log_level_error",
                "ERROR level converts correctly"
            )

        except Exception as e:
            self.add_result(
                "log_level_conversion",
                False,
                f"Log level conversion failed: {str(e)}"
            )

    def test_create_log_directory(self):
        """Test log directory creation."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                log_path = os.path.join(tmpdir, "logs", "test.log")

                # Create directory
                create_log_directory(log_path)

                # Verify directory exists
                log_dir = os.path.dirname(log_path)
                self.assert_true(
                    os.path.exists(log_dir),
                    "log_directory_created",
                    "Log directory is created successfully"
                )

        except Exception as e:
            self.add_result(
                "log_directory_creation",
                False,
                f"Log directory creation failed: {str(e)}"
            )

    def test_setup_logger(self):
        """Test logger setup."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                log_path = os.path.join(tmpdir, "test.log")

                config = {
                    'enable_logging': True,
                    'log_path': log_path,
                    'log_level': 'INFO',
                    'log_rotation': 3
                }

                logger = setup_logger(config, debug=False)

                self.assert_not_none(
                    logger,
                    "logger_setup",
                    "Logger is created successfully"
                )

                self.assert_equal(
                    logger.name,
                    LOGGER_NAME,
                    "logger_name",
                    "Logger has correct name"
                )

                self.assert_equal(
                    logger.level,
                    logging.INFO,
                    "logger_level",
                    "Logger has correct level"
                )

        except Exception as e:
            self.add_result(
                "logger_setup",
                False,
                f"Logger setup failed: {str(e)}"
            )

    def test_setup_logger_debug_mode(self):
        """Test logger setup in debug mode."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                log_path = os.path.join(tmpdir, "test_debug.log")

                config = {
                    'enable_logging': True,
                    'log_path': log_path,
                    'log_level': 'INFO'
                }

                logger = setup_logger(config, debug=True)

                self.assert_equal(
                    logger.level,
                    logging.DEBUG,
                    "logger_debug_level",
                    "Logger level is set to DEBUG when debug=True"
                )

        except Exception as e:
            self.add_result(
                "logger_debug_mode",
                False,
                f"Logger debug mode setup failed: {str(e)}"
            )

    def test_setup_logger_disabled(self):
        """Test logger when logging is disabled."""
        try:
            config = {
                'enable_logging': False
            }

            logger = setup_logger(config, debug=False)

            self.assert_not_none(
                logger,
                "logger_disabled",
                "Logger returns even when disabled"
            )

            self.assert_equal(
                logger.name,
                LOGGER_NAME,
                "logger_disabled_name",
                "Disabled logger has correct name"
            )

        except Exception as e:
            self.add_result(
                "logger_disabled",
                False,
                f"Disabled logger setup failed: {str(e)}"
            )

    def test_get_logger(self):
        """Test getting logger instance."""
        try:
            logger = get_logger()

            self.assert_not_none(
                logger,
                "get_logger",
                "get_logger returns a logger instance"
            )

            self.assert_equal(
                logger.name,
                LOGGER_NAME,
                "get_logger_name",
                "Retrieved logger has correct name"
            )

        except Exception as e:
            self.add_result(
                "get_logger",
                False,
                f"Getting logger failed: {str(e)}"
            )


if __name__ == "__main__":
    test_suite = TestLogging()
    test_suite.run()
    passed, failed = test_suite.report()
    sys.exit(0 if failed == 0 else 1)
