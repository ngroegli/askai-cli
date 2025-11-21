"""
Core business logic for AskAI CLI.

This package contains the main business logic components organized by functionality:
- ai: AI service integration and clients
- patterns: Pattern management system
- questions: Question processing
- chat: Chat management
- messaging: Message building utilities
"""

from .ai import AIService, OpenRouterClient
from .patterns import PatternManager, PatternConfiguration, PatternInput, PatternOutput
from .questions import QuestionProcessor
from .chat import ChatManager
from .messaging import MessageBuilder

__all__ = [
    'AIService',
    'OpenRouterClient',
    'PatternManager',
    'PatternConfiguration',
    'PatternInput',
    'PatternOutput',
    'QuestionProcessor',
    'ChatManager',
    'MessageBuilder'
]
