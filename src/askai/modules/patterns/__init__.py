"""
Patterns package for AskAI CLI.

This package implements the pattern system for configuring AI prompts,
managing inputs and outputs, and specialized use cases through predefined templates.
"""
from .pattern_configuration import (
    PatternConfiguration,
    PatternPurpose,
    PatternFunctionality,
    ModelConfiguration
)
from .pattern_inputs import PatternInput, InputType
from .pattern_outputs import PatternOutput
from .pattern_manager import PatternManager

__all__ = [
    'PatternConfiguration',
    'PatternPurpose',
    'PatternFunctionality',
    'ModelConfiguration',
    'PatternInput',
    'InputType',
    'PatternOutput',
    'PatternManager'
]
