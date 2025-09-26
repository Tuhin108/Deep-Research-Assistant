import streamlit as st
from duckduckgo_search import DDGS
from typing import List, Dict, Optional
import time

class DDGSearchService:
    """Service for performing DuckDuckGo web searches"""
    
    def __init__(self, max_results: int = 10):
        self.max_results = max_results
    
    def search_web(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Perform web search using DuckDuckGo

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search results with title, url, and snippet
        """
        try:
            results_limit = max_results or self.max_results

            # Perform search with rate limiting
            results = []
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=results_limit)

            for result in search_results:
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('href', ''),
                    'snippet': result.get('body', ''),
                    'source': 'DuckDuckGo'
                })

            return results

        except Exception as e:
            st.error(f"Error performing web search: {str(e)}")
            return []
    
    def search_news(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Perform news search using DuckDuckGo

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of news results
        """
        try:
            results_limit = max_results or self.max_results

            results = []
            with DDGS() as ddgs:
                news_results = ddgs.news(query, max_results=results_limit)

            for result in news_results:
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'snippet': result.get('body', ''),
                    'date': result.get('date', ''),
                    'source': result.get('source', 'News')
                })

            return results

        except Exception as e:
            st.error(f"Error performing news search: {str(e)}")
            return []
