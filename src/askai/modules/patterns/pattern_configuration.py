"""
Configuration classes for defining AI patterns and their behavior.

This module contains the classes needed to configure AI interaction patterns,
including model configurations, pattern purposes, and functionalities.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from askai.shared.utils import print_error_or_warnings


class ModelProvider(Enum):
    """
    Enumeration of supported AI model providers.

    Defines the different AI service providers that can be used
    for generating responses and processing queries.
    """
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    CUSTOM = "custom"

@dataclass
class ModelConfiguration:
    """
    Configuration for an AI model with customizable parameters.

    This class holds the complete configuration for an AI model, including
    the provider, model name, and various generation parameters that control
    the behavior of the AI responses.
    """
    provider: Union[str, ModelProvider]
    model_name: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    custom_parameters: Optional[Dict[str, Any]] = None
    web_search: bool = False
    web_search_context: str = "medium"  # low, medium, high
    web_plugin: bool = False
    web_max_results: int = 5
    web_search_prompt: Optional[str] = None

    def __post_init__(self):
        """Convert provider to ModelProvider enum if it's a string."""
        # Handle the provider conversion safely
        if hasattr(self.provider, 'value'):
            # Already a ModelProvider enum
            provider_str = self.provider.value.lower()  # type: ignore
        else:
            # Convert to string first
            provider_str = str(self.provider).lower()
        try:
            self.provider = ModelProvider(provider_str)
        except ValueError:
            for p in ModelProvider:
                if p.value.lower() == provider_str:
                    self.provider = p
                    break
            else:
                self.provider = ModelProvider.OPENROUTER

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelConfiguration':
        """Create a ModelConfiguration instance from a dictionary."""
        return cls(
            provider=data.get('provider', 'openrouter'),
            model_name=data.get('model_name') or "",
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens'),
            stop_sequences=data.get('stop_sequences'),
            custom_parameters=data.get('custom_parameters'),
            web_search=data.get('web_search', False),
            web_search_context=data.get('web_search_context', 'medium'),
            web_plugin=data.get('web_plugin', False),
            web_max_results=data.get('web_max_results', 5),
            web_search_prompt=data.get('web_search_prompt')
        )

    def get_web_search_options(self):
        """Get web search options for non-plugin search."""
        if self.web_search:
            return {"search_context_size": self.web_search_context}
        return None

    def get_web_plugin_config(self) -> Optional[Dict[str, Any]]:
        """Get web plugin configuration."""
        if self.web_plugin:
            config: Dict[str, Any] = {"max_results": self.web_max_results}
            if self.web_search_prompt:
                config["search_prompt"] = self.web_search_prompt
            return config
        return None

@dataclass
class PatternPurpose:
    """
    Defines the purpose and intent of an interaction pattern.

    Contains a name and description that explain what the pattern
    is intended to accomplish and what problem it solves.
    """
    name: str
    description: str

    @classmethod
    def from_text(cls, name: str, description: str) -> 'PatternPurpose':
        """Create a PatternPurpose instance from text content."""
        return cls(
            name=name,
            description=description
        )

@dataclass
class PatternFunctionality:
    """
    Describes the specific capabilities of an interaction pattern.

    Contains a list of features that the pattern provides, allowing users
    to understand the full range of its functionality.
    """
    features: List[str]

    @classmethod
    def from_text(cls, content: str) -> 'PatternFunctionality':
        """Create a PatternFunctionality instance from markdown bullet points."""
        # Extract bullet points, removing empty lines and stripping whitespace
        features = [line.strip('* ').strip() for line in content.split('\n')
                   if line.strip().startswith('*')]
        return cls(features=features)

@dataclass
class PatternConfiguration:
    """
    Complete configuration for an AI interaction pattern.

    Combines purpose, functionality, model configuration, and additional
    parameters to define how the AI should behave for a specific
    interaction pattern. This is the main configuration class that brings
    together all aspects of a pattern definition.
    """
    purpose: PatternPurpose
    functionality: PatternFunctionality
    model: Optional[ModelConfiguration] = None
    format_instructions: Optional[str] = None  # Custom formatting instructions for the AI
    example_conversation: Optional[List[Dict[str, str]]] = None  # Example interactions
    max_context_length: Optional[int] = None  # Maximum context length to maintain

    @classmethod
    def from_components(cls, purpose: PatternPurpose, functionality: PatternFunctionality,
                       model_config: Optional[Dict[str, Any]] = None,
                       format_instructions: Optional[str] = None,
                       example_conversation: Optional[List[Dict[str, str]]] = None,
                       max_context_length: Optional[int] = None) -> 'PatternConfiguration':
        """Create a PatternConfiguration instance from its components."""
        model = None
        if model_config and 'model' in model_config:
            try:
                model = ModelConfiguration.from_dict(model_config['model'])
            except Exception as e:
                print_error_or_warnings(f"Error creating model configuration: {str(e)}")

        return cls(
            purpose=purpose,
            functionality=functionality,
            model=model,
            format_instructions=format_instructions,
            example_conversation=example_conversation,
            max_context_length=max_context_length
        )
