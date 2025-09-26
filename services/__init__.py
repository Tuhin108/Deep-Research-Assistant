"""
Deep Research Assistant Services Package

This package contains all the backend services for the Deep Research Assistant:
- DDGSearchService: DuckDuckGo web and news search
- ContentParser: Web page content extraction  
- EmbeddingService: Text embedding generation
- VectorStore: FAISS-based semantic search
- OCRService: PDF and image text extraction
- GeminiClient: Google Gemini LLM integration
"""

from .ddg_search import DDGSearchService
from .parser import ContentParser
from .embeddings import EmbeddingService
from .vector_store import VectorStore
from .ocr_utils import OCRService
from .gemini_client import GeminiClient

__all__ = [
    'DDGSearchService',
    'ContentParser', 
    'EmbeddingService',
    'VectorStore',
    'OCRService',
    'GeminiClient'
]

__version__ = '1.0.0'