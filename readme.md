# 🔍 Deep Research Assistant

An AI-powered research assistant that helps you discover, extract, and analyze information from multiple sources using advanced semantic search and large language models.

## 🌟 Features

- **Web Search**: DuckDuckGo integration for web and news search
- **Content Extraction**: Smart parsing of web pages, PDFs, and images (OCR)
- **Semantic Search**: Vector-based similarity search using sentence transformers
- **AI Analysis**: Powered by Google's Gemini 2.5 Flash LLM
- **Document Upload**: Support for PDF and image file uploads
- **Scriptures & Old Books**: Access to public domain texts from Project Gutenberg and Internet Archive
- **Research Summaries**: Comprehensive AI-generated research summaries

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Gemini API key

### Installation

1. **Clone or create the project directory:**
```bash
mkdir deep-research-assistant
cd deep-research-assistant
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```
*Note: EasyOCR (for OCR functionality) is included in requirements.txt and will be installed automatically.*

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env file and add your Google API key
```

5. **Get Google Gemini API Key:**
- Visit: https://ai.google.dev/
- Create an account and generate an API key
- Add it to your `.env` file

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
deep-research-assistant/
├── app.py                 # Main Streamlit application
├── services/              # Backend services
│   ├── __init__.py
│   ├── corpus_loader.py  # Scriptures and old books loader
│   ├── ddg_search.py     # DuckDuckGo search
│   ├── embeddings.py     # Sentence transformer embeddings
│   ├── gemini_client.py  # Gemini LLM client
│   ├── logger.py         # Logging utilities
│   ├── ocr_utils.py      # PDF/Image OCR
│   ├── parser.py         # Web content parser
│   └── vector_store.py   # FAISS vector storage
├── requirements.txt      # Python dependencies
├── test_corpus.py        # Corpus loader tests
├── test_search.py        # Search functionality tests
├── TODO.md               # Project tasks and notes
├── .env                  # Environment variables
└── README.md            # This file
```

## 🔧 Usage

### 1. Research a Topic
- Enter your research topic in the "Research Topic" tab
- Configure search settings in the sidebar
- Click "Start Research" to begin automated research

### 2. Upload Files
- Upload PDFs or images in the "Upload Files" tab
- The system will extract text using OCR
- Content is automatically added to the vector store

### 3. Semantic Search
- Use natural language to search through your research
- Find relevant content using semantic similarity

### 4. Ask Questions
- Ask specific questions about your research
- Get AI-powered answers with source citations

### 5. Generate Summaries
- Create comprehensive research summaries
- Get suggested follow-up questions

### 6. Scriptures & Old Books
- Fetch public domain texts from Project Gutenberg or Internet Archive
- Upload local text files for analysis
- Content is automatically embedded and added to the vector store

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional
SENTENCE_TRANSFORMERS_HOME=/path/to/cache
```

### Sidebar Settings
- **Max search results**: Number of web/news results to fetch
- **Max URLs to parse**: Number of web pages to extract content from  
- **Text chunk size**: Size of text chunks for embeddings

## 🧠 How It Works

1. **Search Phase**: Performs web and news searches using DuckDuckGo
2. **Extraction Phase**: Extracts full text content from discovered URLs
3. **Embedding Phase**: Generates semantic embeddings using sentence transformers
4. **Storage Phase**: Stores embeddings in FAISS vector database
5. **Query Phase**: Allows semantic search and AI-powered Q&A

## 🛠️ Technologies Used

- **Frontend**: Streamlit
- **Search**: DuckDuckGo Search API
- **Web Scraping**: Newspaper3k + BeautifulSoup4
- **OCR**: EasyOCR + pdf2image
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Store**: FAISS
- **LLM**: Google Gemini 2.5 Flash
- **PDF Processing**: pdf2image + Pillow

## 📝 Troubleshooting

### Common Issues

**1. FAISS installation issues**
```bash
# Use CPU version for compatibility
pip install faiss-cpu
```

**3. Memory issues with large documents**
- Reduce chunk size in sidebar settings
- Limit number of URLs to parse

**4. API rate limiting**
- Reduce max search results
- Add delays between requests

### Dependencies Issues

If you encounter dependency conflicts, try:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

If you encounter any issues, please check the troubleshooting section or create an issue in the project repository.