"""
Unit tests for pattern configuration.
"""
import os
import sys

# Setup paths for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, os.path.join(project_root, "tests"))

# pylint: disable=wrong-import-position,import-error
from unit.test_base import BaseUnitTest
from askai.core.patterns.configuration import (
    ModelProvider,
    ModelConfiguration,
    PatternPurpose,
    PatternFunctionality,
    PatternConfiguration
)


class TestPatternConfiguration(BaseUnitTest):
    """Test pattern configuration classes."""

    def run(self):
        """Run all pattern configuration tests."""
        self.test_model_provider_enum()
        self.test_model_configuration()
        self.test_model_configuration_from_dict()
        self.test_model_configuration_web_search()
        self.test_pattern_purpose()
        self.test_pattern_functionality()
        self.test_pattern_configuration()
        return self.results

    def test_model_provider_enum(self):
        """Test ModelProvider enum."""
        try:
            self.assert_equal(
                ModelProvider.OPENAI.value,
                "openai",
                "model_provider_openai",
                "OpenAI provider value is correct"
            )

            self.assert_equal(
                ModelProvider.ANTHROPIC.value,
                "anthropic",
                "model_provider_anthropic",
                "Anthropic provider value is correct"
            )

            self.assert_equal(
                ModelProvider.OPENROUTER.value,
                "openrouter",
                "model_provider_openrouter",
                "OpenRouter provider value is correct"
            )

        except Exception as e:
            self.add_result(
                "model_provider_enum",
                False,
                f"ModelProvider enum test failed: {str(e)}"
            )

    def test_model_configuration(self):
        """Test ModelConfiguration creation."""
        try:
            config = ModelConfiguration(
                provider="openrouter",
                model_name="anthropic/claude-3-sonnet",
                temperature=0.7,
                max_tokens=1000
            )

            self.assert_not_none(
                config,
                "model_config_created",
                "ModelConfiguration is created successfully"
            )

            self.assert_equal(
                config.model_name,
                "anthropic/claude-3-sonnet",
                "model_config_name",
                "Model name is set correctly"
            )

            self.assert_equal(
                config.temperature,
                0.7,
                "model_config_temperature",
                "Temperature is set correctly"
            )

            self.assert_equal(
                config.max_tokens,
                1000,
                "model_config_max_tokens",
                "Max tokens is set correctly"
            )

        except Exception as e:
            self.add_result(
                "model_configuration",
                False,
                f"ModelConfiguration test failed: {str(e)}"
            )

    def test_model_configuration_from_dict(self):
        """Test ModelConfiguration from dictionary."""
        try:
            data = {
                'provider': 'openrouter',
                'model_name': 'gpt-4',
                'temperature': 0.5,
                'max_tokens': 2000,
                'web_search': True
            }

            config = ModelConfiguration.from_dict(data)

            self.assert_not_none(
                config,
                "model_config_from_dict",
                "ModelConfiguration is created from dict"
            )

            self.assert_equal(
                config.model_name,
                "gpt-4",
                "model_config_dict_name",
                "Model name from dict is correct"
            )

            self.assert_equal(
                config.web_search,
                True,
                "model_config_web_search",
                "Web search flag is set correctly"
            )

        except Exception as e:
            self.add_result(
                "model_configuration_from_dict",
                False,
                f"ModelConfiguration from_dict test failed: {str(e)}"
            )

    def test_model_configuration_web_search(self):
        """Test ModelConfiguration web search options."""
        try:
            config = ModelConfiguration(
                provider="openrouter",
                model_name="test-model",
                web_search=True,
                web_search_context="high"
            )

            options = config.get_web_search_options()

            self.assert_not_none(
                options,
                "model_config_web_options",
                "Web search options are returned"
            )

            self.assert_equal(
                options.get('search_context_size'),
                "high",
                "model_config_web_context",
                "Web search context size is correct"
            )

        except Exception as e:
            self.add_result(
                "model_configuration_web_search",
                False,
                f"ModelConfiguration web search test failed: {str(e)}"
            )

    def test_pattern_purpose(self):
        """Test PatternPurpose creation."""
        try:
            purpose = PatternPurpose.from_text(
                name="Test Purpose",
                description="This is a test purpose description"
            )

            self.assert_not_none(
                purpose,
                "pattern_purpose_created",
                "PatternPurpose is created successfully"
            )

            self.assert_equal(
                purpose.name,
                "Test Purpose",
                "pattern_purpose_name",
                "Purpose name is set correctly"
            )

            self.assert_equal(
                purpose.description,
                "This is a test purpose description",
                "pattern_purpose_description",
                "Purpose description is set correctly"
            )

        except Exception as e:
            self.add_result(
                "pattern_purpose",
                False,
                f"PatternPurpose test failed: {str(e)}"
            )

    def test_pattern_functionality(self):
        """Test PatternFunctionality creation."""
        try:
            content = """* Feature 1
* Feature 2
* Feature 3"""

            functionality = PatternFunctionality.from_text(content)

            self.assert_not_none(
                functionality,
                "pattern_functionality_created",
                "PatternFunctionality is created successfully"
            )

            self.assert_equal(
                len(functionality.features),
                3,
                "pattern_functionality_count",
                "Correct number of features parsed"
            )

            self.assert_equal(
                functionality.features[0],
                "Feature 1",
                "pattern_functionality_first",
                "First feature is parsed correctly"
            )

        except Exception as e:
            self.add_result(
                "pattern_functionality",
                False,
                f"PatternFunctionality test failed: {str(e)}"
            )

    def test_pattern_configuration(self):
        """Test PatternConfiguration creation."""
        try:
            purpose = PatternPurpose(
                name="Test",
                description="Test description"
            )

            functionality = PatternFunctionality(
                features=["Feature 1", "Feature 2"]
            )

            model_config = ModelConfiguration(
                provider="openrouter",
                model_name="test-model"
            )

            pattern_config = PatternConfiguration(
                purpose=purpose,
                functionality=functionality,
                model=model_config
            )

            self.assert_not_none(
                pattern_config,
                "pattern_config_created",
                "PatternConfiguration is created successfully"
            )

            self.assert_not_none(
                pattern_config.purpose,
                "pattern_config_has_purpose",
                "PatternConfiguration has purpose"
            )

            self.assert_not_none(
                pattern_config.functionality,
                "pattern_config_has_functionality",
                "PatternConfiguration has functionality"
            )

            self.assert_not_none(
                pattern_config.model,
                "pattern_config_has_model",
                "PatternConfiguration has model config"
            )

        except Exception as e:
            self.add_result(
                "pattern_configuration",
                False,
                f"PatternConfiguration test failed: {str(e)}"
            )


if __name__ == "__main__":
    test_suite = TestPatternConfiguration()
    test_suite.run()
    passed, failed = test_suite.report()
    sys.exit(0 if failed == 0 else 1)
