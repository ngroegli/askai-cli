"""Route definitions for the API."""

from .questions import questions_ns
from .health import health_ns
from .patterns import patterns_ns
from .openrouter import openrouter_ns
from .config import config_ns

__all__ = ['questions_ns', 'health_ns', 'patterns_ns', 'openrouter_ns', 'config_ns']
