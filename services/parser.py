import requests
from bs4 import BeautifulSoup
from newspaper import Article
import streamlit as st
from typing import Optional, Dict, List
import time
from urllib.parse import urljoin, urlparse
import re

class ContentParser:
    """Service for parsing various types of content"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_from_url(self, url: str) -> Dict[str, str]:
        """
        Extract text content from a web URL
        
        Args:
            url: URL to extract content from
            
        Returns:
            Dictionary with extracted content and metadata
        """
        try:
            # First try with newspaper3k for better article extraction
            try:
                article = Article(url)
                article.download()
                article.parse()
                
                if article.text and len(article.text.strip()) > 100:
                    return {
                        'url': url,
                        'title': article.title or 'Untitled',
                        'content': article.text,
                        'summary': article.summary or '',
                        'authors': ', '.join(article.authors) if article.authors else '',
                        'publish_date': str(article.publish_date) if article.publish_date else '',
                        'method': 'newspaper3k'
                    }
            except Exception as e:
                st.warning(f"Newspaper3k failed for {url}: {str(e)}")
            
            # Fallback to manual parsing with BeautifulSoup
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Extract title
            title = ""
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            else:
                h1_element = soup.find('h1')
                if h1_element:
                    title = h1_element.get_text().strip()
            
            # Extract main content
            content_selectors = [
                'article', 'main', '.content', '.post-content', 
                '.entry-content', '.article-content', '#content'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = '\n'.join([elem.get_text().strip() for elem in elements])
                    break
            
            # If no specific content area found, get all paragraph text
            if not content:
                paragraphs = soup.find_all('p')
                content = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            # Clean up the content
            content = re.sub(r'\n\s*\n', '\n\n', content)
            content = re.sub(r'\s+', ' ', content)
            
            return {
                'url': url,
                'title': title or 'Untitled',
                'content': content,
                'summary': content[:500] + '...' if len(content) > 500 else content,
                'authors': '',
                'publish_date': '',
                'method': 'beautifulsoup'
            }
            
        except Exception as e:
            st.error(f"Error extracting content from {url}: {str(e)}")
            return {
                'url': url,
                'title': 'Error',
                'content': f'Failed to extract content: {str(e)}',
                'summary': '',
                'authors': '',
                'publish_date': '',
                'method': 'error'
            }
    
    def extract_multiple_urls(self, urls: List[str], progress_callback=None) -> List[Dict[str, str]]:
        """
        Extract content from multiple URLs with progress tracking
        
        Args:
            urls: List of URLs to process
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of extracted content dictionaries
        """
        results = []
        
        for i, url in enumerate(urls):
            if progress_callback:
                progress_callback(i + 1, len(urls), url)
            
            result = self.extract_from_url(url)
            results.append(result)
            
            # Small delay to be respectful to servers
            time.sleep(0.5)
        
        return results
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove common unwanted patterns
        text = re.sub(r'Cookie.*?policy.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Accept.*?cookies.*?\n', '', text, flags=re.IGNORECASE)
        
        return text.strip()