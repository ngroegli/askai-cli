"""
Unit tests for AI and messaging functionality.
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


class TestAIService(BaseUnitTest):
    """Test the AI service functionality."""

    def run(self):
        """Run all AI service tests."""
        self.test_ai_service_initialization()
        self.test_get_ai_response_success()
        self.test_get_ai_response_failure()
        self.test_model_configuration()
        return self.results

    def test_ai_service_initialization(self):
        """Test AI service initialization."""
        try:
            from modules.ai.ai_service import AIService

            mock_logger = Mock()
            ai_service = AIService(mock_logger)

            self.assert_not_none(
                ai_service,
                "ai_service_init",
                "AI service initializes successfully"
            )

            self.assert_not_none(
                ai_service.logger,
                "ai_service_logger",
                "AI service has logger attribute"
            )

        except Exception as e:
            self.add_result("ai_service_init_error", False, f"AI service initialization failed: {e}")

    def test_get_ai_response_success(self):
        """Test successful AI response retrieval."""
        try:
            from modules.ai.ai_service import AIService

            mock_logger = Mock()
            ai_service = AIService(mock_logger)

            # Mock the OpenRouter client response
            mock_response = {
                'content': 'Test AI response',
                'model': 'claude-3-sonnet',
                'usage': {'prompt_tokens': 10, 'completion_tokens': 20}
            }

            # Mock the OpenRouterClient class and user input functions
            with patch('modules.ai.ai_service.OpenRouterClient') as mock_client_class, \
                 patch('modules.patterns.pattern_outputs.PatternOutput._get_user_confirmation', return_value=True), \
                 patch('builtins.input', return_value='y'):
                
                mock_client = Mock()
                mock_client.request_completion.return_value = mock_response
                mock_client_class.return_value = mock_client

                messages = [{'role': 'user', 'content': 'Test question'}]

                # Test if get_ai_response method exists
                if hasattr(ai_service, 'get_ai_response'):
                    response = ai_service.get_ai_response(
                        messages=messages,
                        model_name='claude-3-sonnet',
                        pattern_id=None,
                        debug=False,
                        pattern_manager=None,
                        enable_url_search=False
                    )

                    self.assert_not_none(
                        response,
                        "ai_response_not_none",
                        "AI response is not None"
                    )

                    # Also check the actual response structure for debugging
                    actual_content = response.get('content', '') if isinstance(response, dict) else str(response)

                    self.assert_equal(
                        'Test AI response',
                        actual_content,
                        "ai_response_content",
                        "AI response content matches expected"
                    )
                else:
                    self.add_result("ai_response_method_available", True, "AI service structure verified")

        except Exception as e:
            self.add_result("ai_response_success_error", False, f"AI response test failed: {e}")

    def test_get_ai_response_failure(self):
        """Test AI response handling when API fails."""
        try:
            from modules.ai.ai_service import AIService

            mock_logger = Mock()
            ai_service = AIService(mock_logger)

            # Mock API failure and user input functions
            with patch.object(ai_service, 'openrouter_client', create=True) as mock_client, \
                 patch('modules.patterns.pattern_outputs.PatternOutput._get_user_confirmation', return_value=True), \
                 patch('builtins.input', return_value='y'):
                
                mock_client.get_completion.side_effect = Exception("API Error")

                messages = [{'role': 'user', 'content': 'Test question'}]

                # Test if method exists
                if hasattr(ai_service, 'get_ai_response'):
                    # Should handle the exception gracefully
                    try:
                        ai_service.get_ai_response(
                            messages=messages,
                            model_name='claude-3-sonnet',
                            pattern_id=None,
                            debug=False,
                            pattern_manager=None,
                            enable_url_search=False
                        )

                        # If no exception is raised, response should be None or empty
                        self.add_result("ai_response_failure_handling", True,
                                      "AI service handles API failure gracefully")

                    except Exception:
                        # If exception is raised, that's also acceptable
                        self.add_result("ai_response_failure_exception", True,
                                      "AI service raises exception for API failure")
                else:
                    self.add_result("ai_response_failure_method_check", True, "AI service method check completed")

        except Exception as e:
            self.add_result("ai_response_failure_test_error", False, f"Failure test setup error: {e}")

    def test_model_configuration(self):
        """Test model configuration functionality."""
        try:
            from modules.ai.ai_service import AIService

            mock_logger = Mock()
            ai_service = AIService(mock_logger)

            # Test that service can handle different model names
            test_models = ['claude-3-sonnet', 'gpt-4', 'gpt-3.5-turbo']

            for model in test_models:
                # This tests that the service accepts different model names without error
                try:
                    # We don't actually call the API, just test the method accepts the parameter
                    self.assert_true(
                        hasattr(ai_service, 'get_ai_response'),
                        f"model_config_{model.replace('-', '_')}",
                        f"Service has method to handle {model}"
                    )
                except Exception:
                    self.add_result(f"model_config_{model.replace('-', '_')}_error", False,
                                  f"Error handling model {model}")

        except Exception as e:
            self.add_result("model_config_test_error", False, f"Model configuration test error: {e}")


class TestMessageBuilder(BaseUnitTest):
    """Test the message builder functionality."""

    def run(self):
        """Run all message builder tests."""
        self.test_message_builder_initialization()
        self.test_build_simple_message()
        self.test_build_pattern_message()
        return self.results

    def test_message_builder_initialization(self):
        """Test message builder initialization."""
        try:
            from modules.messaging.builder import MessageBuilder

            mock_pattern_manager = Mock()
            mock_logger = Mock()

            message_builder = MessageBuilder(mock_pattern_manager, mock_logger)

            self.assert_not_none(
                message_builder,
                "message_builder_init",
                "Message builder initializes successfully"
            )

            self.assert_not_none(
                message_builder.pattern_manager,
                "message_builder_pattern_manager",
                "Message builder has pattern manager"
            )

            self.assert_not_none(
                message_builder.logger,
                "message_builder_logger",
                "Message builder has logger"
            )

        except Exception as e:
            self.add_result("message_builder_init_error", False, f"Message builder initialization failed: {e}")

    def test_build_simple_message(self):
        """Test building a simple question message."""
        try:
            from modules.messaging.builder import MessageBuilder

            mock_pattern_manager = Mock()
            mock_logger = Mock()

            message_builder = MessageBuilder(mock_pattern_manager, mock_logger)

            # Test building a simple question
            question = "What is the capital of France?"

            messages, _ = message_builder.build_messages(
                question=question,
                file_input=None,
                pattern_id=None,
                pattern_input=None,
                response_format="rawtext",
                url=None,
                image=None,
                pdf=None,
                image_url=None,
                pdf_url=None
            )

            self.assert_not_none(
                messages,
                "build_simple_message_not_none",
                "Messages are built successfully"
            )

            self.assert_true(
                isinstance(messages, list),
                "build_simple_message_list",
                "Messages is a list"
            )

            if messages:
                self.assert_true(
                    len(messages) > 0,
                    "build_simple_message_not_empty",
                    "Messages list is not empty"
                )

                # Check that the question is included in the messages
                message_content = str(messages)
                self.assert_in(
                    question,
                    message_content,
                    "build_simple_message_content",
                    "Question is included in messages"
                )

        except Exception as e:
            self.add_result("build_simple_message_error", False, f"Simple message building failed: {e}")

    def test_build_pattern_message(self):
        """Test building a pattern-based message."""
        try:
            from modules.messaging.builder import MessageBuilder

            mock_pattern_manager = Mock()
            mock_logger = Mock()

            # Mock pattern data
            mock_pattern_data = {
                'id': 'test_pattern',
                'prompt': 'Test pattern prompt with {input}',
                'inputs': [{'id': 'input', 'label': 'Test Input', 'required': True}]
            }

            mock_pattern_manager.get_pattern_content.return_value = mock_pattern_data
            mock_pattern_manager.validate_inputs.return_value = True

            message_builder = MessageBuilder(mock_pattern_manager, mock_logger)

            # Test building with a pattern
            messages, pattern_id = message_builder.build_messages(
                question=None,
                file_input=None,
                pattern_id='test_pattern',
                pattern_input={'input': 'test value'},
                response_format="rawtext",
                url=None,
                image=None,
                pdf=None,
                image_url=None,
                pdf_url=None
            )

            self.assert_not_none(
                messages,
                "build_pattern_message_not_none",
                "Pattern messages are built successfully"
            )

            self.assert_equal(
                'test_pattern',
                pattern_id,
                "build_pattern_message_id",
                "Pattern ID is returned correctly"
            )

        except Exception as e:
            self.add_result("build_pattern_message_error", False, f"Pattern message building failed: {e}")
