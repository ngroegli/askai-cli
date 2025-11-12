"""
Unit tests for shared configuration functionality - SAFE VERSION.
This version does NOT call actual config loading functions to prevent
any interference with real configuration files.
"""
import importlib.util
import os
import sys

# Setup paths for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "python"))
sys.path.insert(0, os.path.join(project_root, "tests"))

# pylint: disable=wrong-import-position,import-error
from unit.test_base import BaseUnitTest
from shared.config import ASKAI_DIR, CONFIG_PATH
from shared.config.loader import load_config
class TestConfigConstants(BaseUnitTest):
    """Test configuration constants without loading actual config files."""

    def run(self):
        """Run configuration constants tests."""
        self.test_config_constants_exist()
        self.test_path_construction()
        return self.results

    def test_config_constants_exist(self):
        """Test that required configuration constants are defined."""
        try:
            self.assert_not_none(
                ASKAI_DIR,
                "constants_askai_dir",
                "ASKAI_DIR constant is defined"
            )

            self.assert_not_none(
                CONFIG_PATH,
                "constants_config_path",
                "CONFIG_PATH constant is defined"
            )

            self.assert_true(
                isinstance(ASKAI_DIR, str),
                "constants_askai_dir_type",
                "ASKAI_DIR is a string"
            )

            self.assert_true(
                isinstance(CONFIG_PATH, str),
                "constants_config_path_type",
                "CONFIG_PATH is a string"
            )

        except ImportError as e:
            self.add_result("constants_import_error", False,
                          f"Cannot import config constants: {e}")

    def test_path_construction(self):
        """Test that configuration paths are constructed correctly."""
        try:
            # CONFIG_PATH should be within ASKAI_DIR
            self.assert_true(
                CONFIG_PATH.startswith(ASKAI_DIR) or os.path.commonpath([ASKAI_DIR, CONFIG_PATH]) == ASKAI_DIR,
                "path_construction_hierarchy",
                "CONFIG_PATH is within ASKAI_DIR hierarchy"
            )

        except ImportError as e:
            self.add_result("path_construction_error", False,
                          f"Error testing path construction: {e}")


class TestConfigLoaderSafe(BaseUnitTest):
    """Safe tests for config loader that don't actually load config files."""

    def run(self):
        """Run safe configuration loader tests."""
        self.test_config_loader_module_exists()
        self.test_config_loader_function_exists()
        return self.results

    def test_config_loader_module_exists(self):
        """Test that the config loader module can be imported."""
        try:
            # Only test that we can import the module, don't call functions
            module = importlib.util.find_spec("shared.config.loader")
            self.assert_true(
                module is not None,
                "config_loader_module_import",
                "Config loader module imports successfully"
            )

        except ImportError as e:
            self.add_result(
                "config_loader_module_import",
                False,
                f"Cannot import config loader module: {e}"
            )

    def test_config_loader_function_exists(self):
        """Test that the load_config function exists."""
        try:
            # Only test that the function exists, don't call it
            self.assert_true(
                callable(load_config),
                "config_loader_function_callable",
                "load_config function is callable"
            )

        except ImportError as e:
            self.add_result(
                "config_loader_function_exists",
                False,
                f"Cannot import load_config function: {e}"
            )
