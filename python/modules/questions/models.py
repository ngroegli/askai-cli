"""
Question processing models for the AskAI CLI.
Defines data structures for question handling.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class QuestionContext:
    """Context information for processing a question."""
    question: Optional[str] = None
    file_input: Optional[str] = None
    url: Optional[str] = None
    image: Optional[str] = None
    pdf: Optional[str] = None
    image_url: Optional[str] = None
    pdf_url: Optional[str] = None
    response_format: str = "rawtext"
    model: Optional[str] = None
    output_config: Optional[Dict[str, Any]] = None


@dataclass
class QuestionResponse:
    """Response from question processing."""
    content: str
    created_files: Optional[list] = None
    chat_id: Optional[str] = None

    def __post_init__(self):
        if self.created_files is None:
            self.created_files = []
