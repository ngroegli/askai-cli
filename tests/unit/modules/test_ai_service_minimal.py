"""
Minimal unit test for AI service that avoids configuration system.
"""
import os
import sys
from unittest.mock import Mock, patch

# Setup paths for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, os.path.join(project_root, "tests"))

# Set test environment
os.environ['ASKAI_TESTING'] = 'true'

# pylint: disable=wrong-import-position,import-error
from unit.test_base import BaseUnitTest


class TestAIServiceMinimal(BaseUnitTest):
    """Minimal test for AI service that bypasses configuration."""

    def run(self):
        """Run minimal AI service tests."""
        self.test_ai_service_can_be_imported()
        return self.results

    def test_ai_service_can_be_imported(self):
        """Test that AI service can be imported without triggering setup."""
        try:
            # Mock everything before import
            with patch('shared.config.loader.ensure_askai_setup', return_value=True), \
                 patch('shared.config.loader.load_config', return_value={'test': 'config'}), \
                 patch('shared.config.load_config', return_value={'test': 'config'}), \
                 patch('builtins.print'), \
                 patch('os.path.exists', return_value=True), \
                 patch('os.makedirs', return_value=True):

                # Import and instantiate
                from modules.ai.ai_service import AIService

                mock_logger = Mock()
                ai_service = AIService(mock_logger)

                self.assert_not_none(
                    ai_service,
                    "ai_service_import_success",
                    "AI service can be imported and instantiated"
                )

        except Exception as e:
            self.add_result("ai_service_import_error", False, f"Failed to import AI service: {e}")


if __name__ == "__main__":
    test = TestAIServiceMinimal()
    results = test.run()

    # Print results
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{result.name}: {status} - {result.message}")
        if not result.passed:
            print(f"  Details: {result.details}")