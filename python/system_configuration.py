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

    def __post_init__(self):
        """Convert provider to ModelProvider enum if it's a string."""
        if isinstance(self.provider, str):
            try:
                self.provider = ModelProvider(self.provider.lower())
            except ValueError:
                for p in ModelProvider:
                    if p.value.lower() == self.provider.lower():
                        self.provider = p
                        break
                else:
                    self.provider = ModelProvider.OPENROUTER

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelConfiguration':
        """Create a ModelConfiguration instance from a dictionary."""
        return cls(
            provider=data.get('provider', 'openrouter'),
            model_name=data.get('model_name'),
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens'),
            stop_sequences=data.get('stop_sequences'),
            custom_parameters=data.get('custom_parameters')
        )

@dataclass
class SystemPurpose:
    name: str
    description: str

    @classmethod
    def from_text(cls, name: str, description: str) -> 'SystemPurpose':
        """Create a SystemPurpose instance from text content."""
        return cls(
            name=name,
            description=description
        )

@dataclass
class SystemFunctionality:
    features: List[str]
    
    @classmethod
    def from_text(cls, content: str) -> 'SystemFunctionality':
        """Create a SystemFunctionality instance from markdown bullet points."""
        # Extract bullet points, removing empty lines and stripping whitespace
        features = [line.strip('* ').strip() for line in content.split('\n') 
                   if line.strip().startswith('*')]
        return cls(features=features)

@dataclass
class SystemConfiguration:
    purpose: SystemPurpose
    functionality: SystemFunctionality
    model: Optional[ModelConfiguration] = None
    format_instructions: Optional[str] = None  # Custom formatting instructions for the AI
    example_conversation: Optional[List[Dict[str, str]]] = None  # Example interactions
    max_context_length: Optional[int] = None  # Maximum context length to maintain

    @classmethod
    def from_components(cls, purpose: SystemPurpose, functionality: SystemFunctionality, 
                       model_config: Optional[Dict[str, Any]] = None,
                       format_instructions: Optional[str] = None,
                       example_conversation: Optional[List[Dict[str, str]]] = None,
                       max_context_length: Optional[int] = None) -> 'SystemConfiguration':
        """Create a SystemConfiguration instance from its components."""
        model = None
        if model_config and 'model' in model_config:
            try:
                model = ModelConfiguration.from_dict(model_config['model'])
            except Exception as e:
                print(f"Error creating model configuration: {str(e)}")
                
        return cls(
            purpose=purpose,
            functionality=functionality,
            model=model,
            format_instructions=format_instructions,
            example_conversation=example_conversation,
            max_context_length=max_context_length
        )
