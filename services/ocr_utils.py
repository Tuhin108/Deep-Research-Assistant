import streamlit as st
from PIL import Image
import easyocr
from pdf2image import convert_from_bytes, convert_from_path
import io
import tempfile
import os
from typing import List, Optional, Union, Any, Tuple, cast

class OCRService:
    """Service for OCR operations on PDFs and images"""
    
    def __init__(self):
        # Initialize EasyOCR reader
        self.reader = easyocr.Reader(['en'])
    
    def extract_text_from_image(self, image: Union[Image.Image, bytes]) -> str:
        """
        Extract text from an image using OCR
        
        Args:
            image: PIL Image object or image bytes
            
        Returns:
            Extracted text
        """
        try:
            if isinstance(image, bytes):
                image = Image.open(io.BytesIO(image))

            # Use EasyOCR for OCR
            results = cast(List[Tuple[Any, str, float]], self.reader.readtext(image))
            text = ' '.join([item[1] for item in results])
            return text.strip()
            
        except Exception as e:
            st.error(f"Error extracting text from image: {str(e)}")
            return ""
    
    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF bytes using OCR
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            Extracted text from all pages
        """
        try:
            # Convert PDF to images
            images = convert_from_bytes(pdf_bytes, dpi=200)
            
            extracted_text = []
            
            for i, image in enumerate(images):
                st.write(f"Processing page {i + 1}/{len(images)}...")
                
                # Extract text from each page
                page_text = self.extract_text_from_image(image)
                if page_text.strip():
                    extracted_text.append(f"Page {i + 1}:\n{page_text}")
            
            return "\n\n".join(extracted_text)
            
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    def extract_text_from_pdf_file(self, pdf_path: str) -> str:
        """
        Extract text from PDF file using OCR
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text from all pages
        """
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=200)
            
            extracted_text = []
            
            for i, image in enumerate(images):
                st.write(f"Processing page {i + 1}/{len(images)}...")
                
                # Extract text from each page
                page_text = self.extract_text_from_image(image)
                if page_text.strip():
                    extracted_text.append(f"Page {i + 1}:\n{page_text}")
            
            return "\n\n".join(extracted_text)
            
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    def process_uploaded_files(self, uploaded_files) -> List[dict]:
        """
        Process uploaded files and extract text
        
        Args:
            uploaded_files: Streamlit uploaded files
            
        Returns:
            List of extracted content with metadata
        """
        results = []
        
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_type = uploaded_file.type
            
            st.write(f"Processing {file_name}...")
            
            try:
                if file_type.startswith('image/'):
                    # Handle image files
                    image = Image.open(uploaded_file)
                    text = self.extract_text_from_image(image)
                    
                    results.append({
                        'filename': file_name,
                        'type': 'image',
                        'content': text,
                        'title': file_name,
                        'summary': text[:500] + '...' if len(text) > 500 else text
                    })
                    
                elif file_type == 'application/pdf':
                    # Handle PDF files
                    pdf_bytes = uploaded_file.read()
                    text = self.extract_text_from_pdf_bytes(pdf_bytes)
                    
                    results.append({
                        'filename': file_name,
                        'type': 'pdf',
                        'content': text,
                        'title': file_name,
                        'summary': text[:500] + '...' if len(text) > 500 else text
                    })
                    
                else:
                    st.warning(f"Unsupported file type: {file_type}")
                    
            except Exception as e:
                st.error(f"Error processing {file_name}: {str(e)}")
        
        return results