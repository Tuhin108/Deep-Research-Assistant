import streamlit as st
import google.generativeai as genai
import os
from typing import List, Dict, Optional
import time

class GeminiClient:
    """Client for interacting with Gemini 2.5 Flash LLM"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Google API key (if not provided, will try to get from env)
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.model = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini client and model"""
        try:
            if not self.api_key:
                st.error("Google API key not found! Please set GOOGLE_API_KEY in .env file")
                return
            
            # Configure the API key
            genai.configure(api_key=self.api_key)  # type: ignore

            # Initialize the model
            self.model = genai.GenerativeModel(  # type: ignore
                'gemini-2.5-flash',
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            )
            
            st.success("Gemini client initialized successfully!")
            
        except Exception as e:
            st.error(f"Error initializing Gemini client: {str(e)}")
            self.model = None
    
    def generate_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate response using Gemini model
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text
        """
        if not self.model:
            return "Error: Gemini model not initialized"
        
        try:
            # Generate response
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text
            else:
                return "No response generated"
                
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return f"Error: {str(e)}"
    
    def answer_question_with_context(self, question: str, context_documents: List[Dict], max_context_length: int = 4000) -> str:
        """
        Answer a question using provided context documents
        
        Args:
            question: User question
            context_documents: List of relevant document chunks
            max_context_length: Maximum length of context to include
            
        Returns:
            Generated answer
        """
        if not context_documents:
            return self.generate_response(f"Question: {question}")
        
        # Build context from documents
        context_parts = []
        current_length = 0
        
        for doc in context_documents:
            content = doc.get('content', '')
            title = doc.get('title', 'Untitled')
            url = doc.get('url', '')
            
            doc_text = f"Source: {title}"
            if url:
                doc_text += f" ({url})"
            doc_text += f"\nContent: {content}\n"
            
            if current_length + len(doc_text) > max_context_length:
                break
            
            context_parts.append(doc_text)
            current_length += len(doc_text)
        
        context = "\n---\n".join(context_parts)
        
        # Create comprehensive prompt
        prompt = f"""Based on the following research context, please answer the user's question. 
Provide a comprehensive, accurate answer and cite the relevant sources when possible.

RESEARCH CONTEXT:
{context}

QUESTION: {question}

Please provide a detailed answer based on the context above. If the context doesn't contain enough information to fully answer the question, please indicate what information is missing and provide what insights you can based on the available context."""
        
        return self.generate_response(prompt, max_tokens=1500)
    
    def summarize_research(self, documents: List[Dict], topic: str) -> str:
        """
        Generate a research summary from multiple documents
        
        Args:
            documents: List of research documents
            topic: Research topic
            
        Returns:
            Research summary
        """
        if not documents:
            return "No documents provided for summarization."
        
        # Extract key information from documents
        doc_summaries = []
        for doc in documents[:10]:  # Limit to top 10 documents
            title = doc.get('title', 'Untitled')
            content = doc.get('content', '')
            url = doc.get('url', '')
            
            # Truncate content if too long
            if len(content) > 500:
                content = content[:500] + "..."
            
            summary = f"**{title}**"
            if url:
                summary += f" ({url})"
            summary += f"\n{content}"
            
            doc_summaries.append(summary)
        
        combined_content = "\n\n---\n\n".join(doc_summaries)
        
        prompt = f"""Please create a comprehensive research summary about "{topic}" based on the following sources:

{combined_content}

Please provide:
1. An executive summary of the key findings
2. Main themes and insights discovered
3. Important statistics or facts (if any)
4. Different perspectives or viewpoints presented
5. Areas that might need further research

Format the response in a clear, well-structured manner."""
        
        return self.generate_response(prompt, max_tokens=2000)
    
    def generate_follow_up_questions(self, topic: str, documents: List[Dict]) -> List[str]:
        """
        Generate relevant follow-up questions based on research topic and documents
        
        Args:
            topic: Research topic
            documents: List of research documents
            
        Returns:
            List of follow-up questions
        """
        if not documents:
            return []
        
        # Create summary of key points from documents
        doc_summaries = []
        for doc in documents[:5]:  # Limit to top 5 documents
            title = doc.get('title', 'Untitled')
            content = doc.get('content', '')[:300] + "..."  # Truncate for brevity
            doc_summaries.append(f"- {title}: {content}")
        
        combined_summaries = "\n".join(doc_summaries)
        
        prompt = f"""Based on the research about "{topic}" and the following key findings:

{combined_summaries}

Generate 5 relevant follow-up questions that would help deepen understanding of this topic. 
The questions should be:
1. Specific and actionable
2. Build upon the existing research
3. Address different aspects or perspectives
4. Help identify gaps or areas for further investigation

Format as a numbered list:"""
        
        response = self.generate_response(prompt, max_tokens=500)
        
        # Parse questions from response
        questions = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering and clean up
                question = line.split('.', 1)[-1].strip()
                question = line.split('-', 1)[-1].strip() if '-' in line else question
                if question and question.endswith('?'):
                    questions.append(question)
        
        return questions[:5]