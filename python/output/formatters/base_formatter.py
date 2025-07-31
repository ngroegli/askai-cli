"""
Base class for output formatters.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging


class BaseFormatter(ABC):
    """Base class for formatters that format content for different outputs."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize formatter with optional logger.
        
        Args:
            logger: Optional logger for logging messages
        """
        self.logger = logger
    
    @abstractmethod
    def format(self, content: str, **kwargs) -> str:
        """Format content according to specific rules.
        
        Args:
            content: Content to format
            kwargs: Additional formatting options
            
        Returns:
            str: Formatted content
        """
        pass
    
    def _truncate_content(self, content: str, max_length: int = 1000, 
                         ellipsis: str = "...\n[content truncated]") -> str:
        """Truncate content if it exceeds maximum length.
        
        Args:
            content: Content to truncate
            max_length: Maximum length before truncation
            ellipsis: Text to append when truncating
            
        Returns:
            str: Truncated content if needed, original otherwise
        """
        if len(content) > max_length:
            truncated = content[:max_length] + ellipsis
            if self.logger:
                self.logger.info(f"Content truncated from {len(content)} to {max_length} characters")
            return truncated
        return content
