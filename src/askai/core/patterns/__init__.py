"""
Patterns package for AskAI CLI.

This package implements the pattern system for configuring AI prompts,
managing inputs and outputs, and specialized use cases through predefined templates.
"""
from .configuration import (
    PatternConfiguration,
    PatternPurpose,
    PatternFunctionality,
    ModelConfiguration
)
from .inputs import PatternInput, InputType
from .outputs import PatternOutput
from .manager import PatternManager

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
