from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from enum import Enum

class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    CUSTOM = "custom"

@dataclass
class ModelConfiguration:
    provider: ModelProvider
    model_name: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    custom_parameters: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelConfiguration':
        """Create a ModelConfiguration instance from a dictionary."""
        return cls(
            provider=ModelProvider(data['provider']),
            model_name=data['model_name'],
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens'),
            stop_sequences=data.get('stop_sequences'),
            custom_parameters=data.get('custom_parameters')
        )

@dataclass
class SystemConfiguration:
    name: str
    description: str
    model: ModelConfiguration
    format_instructions: Optional[str] = None  # Custom formatting instructions for the AI
    example_conversation: Optional[List[Dict[str, str]]] = None  # Example interactions
    max_context_length: Optional[int] = None  # Maximum context length to maintain

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemConfiguration':
        """Create a SystemConfiguration instance from a dictionary."""
        return cls(
            name=data['name'],
            description=data.get('description', ''),
            model=ModelConfiguration.from_dict(data['model']),
            format_instructions=data.get('format_instructions'),
            example_conversation=data.get('example_conversation'),
            max_context_length=data.get('max_context_length')
        )
