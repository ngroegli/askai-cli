"""
AI service package for AskAI CLI.

This package provides AI model integration services and client implementations
for various AI providers, currently focusing on OpenRouter.
"""
from .service import AIService
from .openrouter import OpenRouterClient

__all__ = ['AIService', 'OpenRouterClient']