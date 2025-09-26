import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import torch

class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding service
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            with st.spinner(f"Loading embedding model: {self.model_name}..."):
                self.model = SentenceTransformer(self.model_name)
            st.success("Embedding model loaded successfully!")
        except Exception as e:
            st.error(f"Error loading embedding model: {str(e)}")
            self.model = None
    
    def generate_embeddings(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text(s)
        
        Args:
            texts: Single text string or list of text strings
            
        Returns:
            Numpy array of embeddings
        """
        if not self.model:
            st.error("Embedding model not loaded!")
            return np.array([])
        
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            # Generate embeddings
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings
            
        except Exception as e:
            st.error(f"Error generating embeddings: {str(e)}")
            return np.array([])
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into chunks for embedding
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to end at a sentence boundary
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                for i in range(end, max(start + chunk_size // 2, end - 100), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    def process_documents_for_embedding(self, documents: List[dict], chunk_size: int = 1000) -> List[dict]:
        """
        Process documents and prepare them for embedding
        
        Args:
            documents: List of document dictionaries
            chunk_size: Size of chunks for long documents
            
        Returns:
            List of processed chunks with metadata
        """
        processed_chunks = []
        
        for doc in documents:
            content = doc.get('content', '')
            if not content:
                continue
            
            # Split long documents into chunks
            chunks = self.chunk_text(content, chunk_size)
            
            for i, chunk in enumerate(chunks):
                chunk_doc = {
                    'content': chunk,
                    'title': doc.get('title', ''),
                    'url': doc.get('url', ''),
                    'source': doc.get('source', ''),
                    'chunk_id': i,
                    'total_chunks': len(chunks),
                    'metadata': {
                        'filename': doc.get('filename', ''),
                        'type': doc.get('type', ''),
                        'authors': doc.get('authors', ''),
                        'publish_date': doc.get('publish_date', '')
                    }
                }
                processed_chunks.append(chunk_doc)
        
        return processed_chunks