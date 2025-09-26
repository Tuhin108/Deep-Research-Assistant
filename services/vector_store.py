# pyright: reportCallIssue = false
import streamlit as st
import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Tuple, Optional
import tempfile

class VectorStore:
    """Service for storing and searching document embeddings using FAISS"""
    
    def __init__(self):
        """Initialize the vector store"""
        self.index = None
        self.documents = []
        self.dimension = None
    
    def create_index(self, embeddings: np.ndarray, documents: List[Dict]):
        """
        Create FAISS index from embeddings and documents
        
        Args:
            embeddings: Numpy array of embeddings
            documents: List of document dictionaries
        """
        try:
            if len(embeddings) == 0:
                st.error("No embeddings provided!")
                return False
            
            # Get embedding dimension
            self.dimension = embeddings.shape[1]
            
            # Create FAISS index (using L2 distance)
            self.index = faiss.IndexFlatL2(self.dimension)  # type: ignore[call-arg]
            
            # Add embeddings to index
            self.index.add(embeddings.astype('float32'))
            
            # Store documents
            self.documents = documents
            
            st.success(f"Vector store created with {len(documents)} documents!")
            return True
            
        except Exception as e:
            st.error(f"Error creating vector store: {str(e)}")
            return False
    
    def add_documents(self, embeddings: np.ndarray, documents: List[Dict]):
        """
        Add new documents to existing index
        
        Args:
            embeddings: Numpy array of new embeddings
            documents: List of new document dictionaries
        """
        try:
            if self.index is None:
                return self.create_index(embeddings, documents)
            
            # Add embeddings to existing index
            self.index.add(embeddings.astype('float32'))  # type: ignore[call-arg]
            
            # Add documents to existing list
            self.documents.extend(documents)
            
            st.success(f"Added {len(documents)} documents to vector store!")
            return True
            
        except Exception as e:
            st.error(f"Error adding documents to vector store: {str(e)}")
            return False
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Search for similar documents using semantic similarity
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            
        Returns:
            List of (document, similarity_score) tuples
        """
        try:
            if self.index is None or len(self.documents) == 0:
                st.warning("Vector store is empty!")
                return []
            
            # Ensure query embedding is 2D
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            # Search in FAISS index
            distances, indices = self.index.search(  # type: ignore
                x=query_embedding.astype('float32'),
                k=min(top_k, len(self.documents))
            )
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.documents):
                    # Convert L2 distance to similarity score (0-1, higher is better)
                    similarity = 1 / (1 + distance)
                    results.append((self.documents[idx], similarity))
            
            return results
            
        except Exception as e:
            st.error(f"Error searching vector store: {str(e)}")
            return []
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        return {
            'num_documents': len(self.documents),
            'dimension': self.dimension,
            'has_index': self.index is not None,
            'index_size': self.index.ntotal if self.index else 0
        }
    
    def save_to_session_state(self):
        """Save vector store to Streamlit session state"""
        try:
            if self.index is not None:
                # Save FAISS index to bytes
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    faiss.write_index(self.index, tmp.name)
                    with open(tmp.name, 'rb') as f:
                        index_bytes = f.read()
                    os.unlink(tmp.name)

                st.session_state['vector_store_data'] = {
                    'index_bytes': index_bytes,
                    'documents': self.documents,
                    'dimension': self.dimension
                }

                st.success("Vector store saved to session!")

        except Exception as e:
            st.error(f"Error saving vector store: {str(e)}")
    
    def load_from_session_state(self):
        """Load vector store from Streamlit session state"""
        try:
            if 'vector_store_data' in st.session_state:
                data = st.session_state['vector_store_data']

                # Load FAISS index from bytes
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    with open(tmp.name, 'wb') as f:
                        f.write(data['index_bytes'])
                    self.index = faiss.read_index(tmp.name)
                    os.unlink(tmp.name)

                self.documents = data['documents']
                self.dimension = data['dimension']

                st.success(f"Vector store loaded with {len(self.documents)} documents!")
                return True

        except Exception as e:
            st.error(f"Error loading vector store: {str(e)}")

        return False
    
    def clear(self):
        """Clear the vector store"""
        self.index = None
        self.documents = []
        self.dimension = None

        if 'vector_store_data' in st.session_state:
            del st.session_state['vector_store_data']

        st.success("Vector store cleared!")
