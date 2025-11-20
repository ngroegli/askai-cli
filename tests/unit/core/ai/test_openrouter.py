"""
Unit tests for OpenRouter API client.
"""
import os
import sys
from unittest.mock import Mock, patch

# Setup paths for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, os.path.join(project_root, "tests"))

# pylint: disable=wrong-import-position,import-error
from unit.test_base import BaseUnitTest
from askai.core.ai.openrouter import OpenRouterClient


class TestOpenRouterClient(BaseUnitTest):
    """Test the OpenRouter client functionality."""

    def run(self):
        """Run all OpenRouter client tests."""
        self.test_client_initialization()
        self.test_get_headers()
        self.test_configure_model_settings()
        self.test_detect_content_types()
        return self.results

    def test_client_initialization(self):
        """Test OpenRouter client initialization."""
        try:
            mock_config = {
                'api_key': 'test-key',
                'base_url': 'https://openrouter.ai/api/v1'
            }

            with patch('askai.utils.config.load_config', return_value=mock_config):
                client = OpenRouterClient(config=mock_config)

                self.assert_not_none(
                    client,
                    "openrouter_client_init",
                    "OpenRouter client initializes successfully"
                )

                self.assert_equal(
                    client.base_url,
                    'https://openrouter.ai/api/v1/',
                    "openrouter_base_url",
                    "Base URL is correctly set with trailing slash"
                )

        except Exception as e:
            self.add_result(
                "openrouter_client_init",
                False,
                f"OpenRouter client initialization failed: {str(e)}"
            )

    def test_get_headers(self):
        """Test getting API headers."""
        try:
            mock_config = {
                'api_key': 'test-key',
                'base_url': 'https://openrouter.ai/api/v1'
            }

            with patch('askai.utils.config.load_config', return_value=mock_config):
                mock_logger = Mock()
                client = OpenRouterClient(config=mock_config, logger=mock_logger)
                # pylint: disable=protected-access
                headers = client._get_headers()

                self.assert_not_none(
                    headers,
                    "headers_exist",
                    "Headers returned from _get_headers"
                )

        except Exception as e:
            self.add_result(
                "openrouter_get_headers",
                False,
                f"Getting headers failed: {str(e)}"
            )

    def test_configure_model_settings(self):
        """Test model configuration settings."""
        try:
            mock_config = {
                'api_key': 'test-key',
                'base_url': 'https://openrouter.ai/api/v1'
            }

            mock_model_config = Mock()
            mock_model_config.model_name = "anthropic/claude-3-sonnet"
            mock_model_config.temperature = 0.7
            mock_model_config.max_tokens = 1000
            mock_model_config.stop_sequences = ["STOP"]

            with patch('askai.utils.config.load_config', return_value=mock_config):
                client = OpenRouterClient(config=mock_config)
                payload = {}
                # pylint: disable=protected-access
                result = client._configure_model_settings(payload, mock_model_config)

                self.assert_equal(
                    result['model'],
                    "anthropic/claude-3-sonnet",
                    "openrouter_model_name",
                    "Model name is set correctly"
                )

                self.assert_equal(
                    result['temperature'],
                    0.7,
                    "openrouter_temperature",
                    "Temperature is set correctly"
                )

                self.assert_equal(
                    result['max_tokens'],
                    1000,
                    "openrouter_max_tokens",
                    "Max tokens is set correctly"
                )

        except Exception as e:
            self.add_result(
                "openrouter_configure_model",
                False,
                f"Model configuration failed: {str(e)}"
            )

    def test_detect_content_types(self):
        """Test content type detection."""
        try:
            mock_config = {
                'api_key': 'test-key',
                'base_url': 'https://openrouter.ai/api/v1'
            }

            with patch('askai.utils.config.load_config', return_value=mock_config):
                client = OpenRouterClient(config=mock_config)

                # Test with multimodal content
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What's in this image?"},
                            {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
                        ]
                    }
                ]

                # pylint: disable=protected-access
                result = client._detect_content_types(messages)

                self.assert_equal(
                    result['has_multimodal'],
                    True,
                    "openrouter_detect_multimodal",
                    "Multimodal content is detected"
                )

        except Exception as e:
            self.add_result(
                "openrouter_detect_content",
                False,
                f"Content type detection failed: {str(e)}"
            )


if __name__ == "__main__":
    test_suite = TestOpenRouterClient()
    test_suite.run()
    passed, failed = test_suite.report()
    sys.exit(0 if failed == 0 else 1)
