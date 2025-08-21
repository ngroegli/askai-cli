"""
Patterns package for AskAI CLI.

This package implements the pattern system for configuring AI prompts, 
managing inputs and outputs, and specialized use cases through predefined templates.
"""
from python.patterns.pattern_configuration import (
    PatternConfiguration,
    PatternPurpose,
    PatternFunctionality,
    ModelConfiguration
)
from python.patterns.pattern_inputs import PatternInput, InputType
from python.patterns.pattern_outputs import PatternOutput
from python.patterns.pattern_manager import PatternManager

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
