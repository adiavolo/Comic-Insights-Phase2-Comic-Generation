"""Backend modules for Comic Insights.

This package contains the core backend functionality for:
- NLP processing and text generation
- Session management
- Image generation and processing
"""

from .nlp_engine import NLPEngine
from .session_manager import SessionManager
from . import img_api

# Create singleton instances
nlp_engine = NLPEngine()
session_manager = SessionManager() 