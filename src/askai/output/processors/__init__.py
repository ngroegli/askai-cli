"""Output processors package.

This package contains specialized processors for handling different aspects
of output processing in the AskAI CLI system.
"""

from .extractor import ContentExtractor
from .pattern import PatternProcessor
from .normalizer import ResponseNormalizer
from .directory import DirectoryManager

__all__ = [
    'ContentExtractor',
    'PatternProcessor',
    'ResponseNormalizer',
    'DirectoryManager'
]
