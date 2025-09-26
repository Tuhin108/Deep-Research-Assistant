import streamlit as st
import os
from dotenv import load_dotenv
import tempfile
import time
from typing import List, Dict

# Load environment variables
load_dotenv()

# Import services
from services.ddg_search import DDGSearchService
from services.parser import ContentParser
from services.embeddings import EmbeddingService
from services.vector_store import VectorStore
from services.ocr_utils import OCRService
from services.gemini_client import GeminiClient
from services.corpus_loader import CorpusService

# Configure Streamlit page
st.set_page_config(
    page_title="Deep Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services in session state
@st.cache_resource
def init_services(api_key: str):
    """Initialize all services"""
    return {
        'search': DDGSearchService(),
        'parser': ContentParser(),
        'embeddings': EmbeddingService(),
        'ocr': OCRService(),
        'gemini': GeminiClient(api_key=api_key),
        'corpus': CorpusService()
    }

def main():
    # Check if API key is provided
    if 'api_key' not in st.session_state or not st.session_state.api_key:
        # Initial state: Show About Us and API key input
        st.title("📖 About Us")
        st.markdown("""
        # 🔍 Deep Research Assistant

        Welcome to the Deep Research Assistant! This powerful tool helps you conduct comprehensive research on any topic using advanced AI and web scraping technologies.

        ## 🌟 Features

        - **Web & News Search**: Automatically search the web and news sources for your research topic
        - **Content Extraction**: Extract full content from relevant web pages
        - **Semantic Search**: Find information using natural language queries
        - **AI-Powered Q&A**: Get intelligent answers to your questions based on research data
        - **File Upload & OCR**: Process PDFs and images for text extraction
        - **Scriptures & Old Books**: Access classic literature from Project Gutenberg and Internet Archive
        - **Vector Embeddings**: Store and search through document embeddings for fast retrieval

        ## 🚀 How to Use

        1. Enter your Gemini API key in the sidebar
        2. Research any topic with our comprehensive search tools
        3. Upload files or add scriptures to expand your knowledge base
        4. Ask questions and get AI-powered answers
        5. Generate summaries of your research findings

        ## 🔧 Technology Stack

        - **Frontend**: Streamlit
        - **AI Model**: Google Gemini 2.5 Flash
        - **Embeddings**: Sentence Transformers
        - **Vector Store**: FAISS
        - **Web Scraping**: BeautifulSoup, Selenium
        - **OCR**: EasyOCR

        Get started by entering your Gemini API key below!
        """)

        # Sidebar for API key input
        with st.sidebar:
            st.header("🔑 API Configuration")
            api_key_input = st.text_input(
                "Enter your Gemini API Key:",
                type="password",
                help="Get your API key from Google AI Studio"
            )

            if st.button("🚀 Start Research Assistant", type="primary"):
                if api_key_input:
                    st.session_state.api_key = api_key_input
                    st.rerun()
                else:
                    st.error("Please enter a valid API key")

        return

    # Main app state
    st.title("🔍 Deep Research Assistant")
    st.markdown("Research any topic with AI-powered web search, content extraction, and semantic analysis")

    # Initialize services with API key
    services = init_services(st.session_state.api_key)

    # Initialize vector store in session state
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = VectorStore()
        st.session_state.vector_store.load_from_session_state()

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Research settings
        st.subheader("🔧 Search Settings")
        max_search_results = st.slider("Max search results", 5, 20, 10)
        max_urls_to_parse = st.slider("Max URLs to parse", 3, 15, 5)
        chunk_size = st.slider("Text chunk size", 500, 2000, 1000)

        # Vector store stats
        st.subheader("📊 Vector Store Stats")
        stats = st.session_state.vector_store.get_stats()
        st.metric("Documents", stats['num_documents'])
        st.metric("Embedding Dimension", stats.get('dimension', 0))

        if st.button("🗑️ Clear Vector Store"):
            st.session_state.vector_store.clear()
            st.rerun()
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔍 Research Topic", 
        "📄 Upload Files", 
        "🧠 Semantic Search", 
        "💬 Ask Questions",
        "📋 Research Summary",
        "📚 Scriptures & Old Books"
    ])
    
    # Tab 1: Research Topic
    with tab1:
        st.header("🔍 Research a Topic")
        
        research_query = st.text_input(
            "Enter your research topic:",
            placeholder="e.g., artificial intelligence in healthcare, climate change impacts, quantum computing"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            search_web = st.checkbox("🌐 Web Search", value=True)
            search_news = st.checkbox("📰 News Search", value=True)
        
        with col2:
            extract_content = st.checkbox("📝 Extract Full Content", value=True)
            generate_embeddings = st.checkbox("🧠 Generate Embeddings", value=True)
        
        if st.button("🚀 Start Research", type="primary"):
            if not research_query:
                st.error("Please enter a research topic!")
                return
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            all_documents = []

            # Initialize results lists
            web_results = []
            news_results = []

            # Step 1: Web Search
            if search_web:
                status_text.text("🔍 Searching the web...")
                progress_bar.progress(10)
                
                web_results = services['search'].search_web(research_query, max_search_results)
                st.success(f"Found {len(web_results)} web results")
                
                with st.expander("🌐 Web Search Results"):
                    for result in web_results[:5]:
                        st.write(f"**{result['title']}**")
                        st.write(f"🔗 {result['url']}")
                        st.write(f"📝 {result['snippet'][:200]}...")
                        st.divider()
            
            # Step 2: News Search
            if search_news:
                status_text.text("📰 Searching news...")
                progress_bar.progress(20)

                news_results = services['search'].search_news(research_query, max_search_results//2)
                st.success(f"Found {len(news_results)} news results")

                with st.expander("📰 News Search Results"):
                    for result in news_results[:3]:
                        st.write(f"**{result['title']}**")
                        st.write(f"🔗 {result['url']}")
                        st.write(f"📅 {result.get('date', 'N/A')}")
                        st.write(f"📝 {result['snippet'][:200]}...")
                        st.divider()

            # Step 2.5: Scriptures & Old Books Search
            status_text.text("📚 Searching scriptures & old books...")
            progress_bar.progress(30)

            book_results = services['corpus'].fetch_from_gutenberg(research_query, max_results=2)
            archive_results = services['corpus'].fetch_from_archive(research_query, max_results=1)

            all_books = book_results + archive_results

            if all_books:
                st.success(f"Found {len(all_books)} scriptures/old books")
                with st.expander("📚 Scriptures & Old Books Results"):
                    for book in all_books:
                        st.write(f"**{book['title']}** ({book['source']})")
                        st.write(book['content'][:500] + "...")
                        st.divider()

                all_documents.extend(all_books)

            # Step 3: Extract Content
            if extract_content:
                status_text.text("📝 Extracting content from URLs...")
                progress_bar.progress(50)
                
                # Combine all URLs
                all_urls = []
                if search_web:
                    all_urls.extend([r['url'] for r in web_results])
                if search_news:
                    all_urls.extend([r['url'] for r in news_results])
                
                # Extract content from top URLs
                urls_to_extract = all_urls[:max_urls_to_parse]
                
                extraction_progress = st.empty()
                
                def progress_callback(current, total, url):
                    extraction_progress.text(f"Extracting {current}/{total}: {url[:50]}...")
                
                extracted_docs = services['parser'].extract_multiple_urls(
                    urls_to_extract, 
                    progress_callback
                )
                
                # Filter successful extractions
                successful_docs = [doc for doc in extracted_docs if len(doc['content']) > 100]
                all_documents.extend(successful_docs)
                
                st.success(f"Successfully extracted content from {len(successful_docs)} URLs")
            
            # Step 4: Generate Embeddings
            if generate_embeddings and all_documents:
                status_text.text("🧠 Generating embeddings...")
                progress_bar.progress(80)
                
                # Process documents for embedding
                processed_chunks = services['embeddings'].process_documents_for_embedding(
                    all_documents, chunk_size
                )
                
                if processed_chunks:
                    # Generate embeddings
                    texts = [chunk['content'] for chunk in processed_chunks]
                    embeddings = services['embeddings'].generate_embeddings(texts)
                    
                    if embeddings.size > 0:
                        # Add to vector store
                        st.session_state.vector_store.add_documents(embeddings, processed_chunks)
                        st.success(f"Added {len(processed_chunks)} document chunks to vector store")
            
            # Step 5: Complete
            status_text.text("✅ Research complete!")
            progress_bar.progress(100)
            time.sleep(1)
            status_text.empty()
            progress_bar.empty()
            
            # Store results in session state
            st.session_state.last_research = {
                'query': research_query,
                'documents': all_documents,
                'timestamp': time.time()
            }
    
    # Tab 2: Upload Files
    with tab2:
        st.header("📄 Upload Files for Analysis")
        
        uploaded_files = st.file_uploader(
            "Upload PDFs or Images",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            help="Upload PDF documents or images for OCR text extraction"
        )
        
        if uploaded_files:
            if st.button("📝 Process Uploaded Files"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Process files
                status_text.text("🔍 Processing uploaded files...")
                extracted_docs = services['ocr'].process_uploaded_files(uploaded_files)
                
                if extracted_docs:
                    progress_bar.progress(50)
                    status_text.text("🧠 Generating embeddings...")
                    
                    # Generate embeddings for uploaded content
                    processed_chunks = services['embeddings'].process_documents_for_embedding(
                        extracted_docs, chunk_size
                    )
                    
                    if processed_chunks:
                        texts = [chunk['content'] for chunk in processed_chunks]
                        embeddings = services['embeddings'].generate_embeddings(texts)
                        
                        if embeddings.size > 0:
                            st.session_state.vector_store.add_documents(embeddings, processed_chunks)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Files processed successfully!")
                    
                    st.success(f"Processed {len(extracted_docs)} files")
                    
                    # Show extracted content preview
                    with st.expander("📄 Extracted Content Preview"):
                        for doc in extracted_docs:
                            st.write(f"**{doc['filename']}** ({doc['type']})")
                            st.write(f"📝 {doc['summary']}")
                            st.divider()
                    
                    time.sleep(2)
                    status_text.empty()
                    progress_bar.empty()
    
    # Tab 3: Semantic Search
    with tab3:
        st.header("🧠 Semantic Search")
        
        if st.session_state.vector_store.get_stats()['num_documents'] == 0:
            st.warning("No documents in vector store. Please research a topic or upload files first.")
            return
        
        search_query = st.text_input(
            "Enter your search query:",
            placeholder="e.g., What are the main benefits? How does it work? Recent developments"
        )
        
        num_results = st.slider("Number of results", 1, 10, 5)
        
        if st.button("🔍 Search") and search_query:
            # Generate query embedding
            query_embedding = services['embeddings'].generate_embeddings([search_query])
            
            if query_embedding.size > 0:
                # Search vector store
                results = st.session_state.vector_store.search(query_embedding, num_results)
                
                if results:
                    st.success(f"Found {len(results)} relevant results")
                    
                    for i, (doc, score) in enumerate(results):
                        with st.expander(f"Result {i+1}: {doc['title'][:50]}... (Score: {score:.3f})"):
                            st.write(f"**Title:** {doc['title']}")
                            st.write(f"**URL:** {doc.get('url', 'N/A')}")
                            st.write(f"**Content:**")
                            st.write(doc['content'][:1000] + "..." if len(doc['content']) > 1000 else doc['content'])
                else:
                    st.warning("No relevant results found.")
    
    # Tab 4: Ask Questions
    with tab4:
        st.header("💬 Ask Questions About Your Research")
        
        if st.session_state.vector_store.get_stats()['num_documents'] == 0:
            st.warning("No research data available. Please research a topic or upload files first.")
            return
        
        question = st.text_area(
            "Ask a question about your research:",
            placeholder="e.g., What are the key findings? Summarize the main points. What are the pros and cons?"
        )
        
        if st.button("🤖 Get Answer") and question:
            with st.spinner("🤔 Thinking..."):
                # Find relevant context
                query_embedding = services['embeddings'].generate_embeddings([question])
                
                if query_embedding.size > 0:
                    # Get relevant documents
                    relevant_docs = st.session_state.vector_store.search(query_embedding, 5)
                    context_documents = [doc for doc, score in relevant_docs]
                    
                    # Generate answer using Gemini
                    answer = services['gemini'].answer_question_with_context(
                        question, context_documents
                    )
                    
                    st.write("### 🤖 AI Answer:")
                    st.write(answer)
                    
                    # Show sources
                    if context_documents:
                        with st.expander("📚 Sources Used"):
                            for i, doc in enumerate(context_documents[:3]):
                                st.write(f"**Source {i+1}:** {doc['title']}")
                                st.write(f"🔗 {doc.get('url', 'N/A')}")
                                st.write(f"📝 {doc['content'][:200]}...")
                                st.divider()
    
    # Tab 5: Research Summary
    with tab5:
        st.header("📋 Research Summary")
        
        if 'last_research' not in st.session_state:
            st.warning("No research data available. Please research a topic first.")
            return
        
        research_info = st.session_state.last_research
        st.write(f"**Research Topic:** {research_info['query']}")
        st.write(f"**Research Date:** {time.ctime(research_info['timestamp'])}")
        st.write(f"**Documents Found:** {len(research_info.get('documents', []))}")
        
        if st.button("📝 Generate Research Summary"):
            with st.spinner("📝 Generating comprehensive summary..."):
                # Get documents from the last research session
                all_docs = research_info.get('documents', [])
                
                if all_docs:
                    topic = research_info['query']
                    summary = services['gemini'].summarize_research(all_docs, topic)
                    
                    st.write("### 📋 Research Summary:")
                    st.write(summary)
                    
                    # Generate follow-up questions
                    st.write("### ❓ Suggested Follow-up Questions:")
                    follow_ups = services['gemini'].generate_follow_up_questions(topic, all_docs[:5])
                    
                    if follow_ups:
                        for i, question in enumerate(follow_ups, 1):
                            st.write(f"{i}. {question}")
                else:
                    st.warning("No documents available for summarization.")

    # Tab 6: Scriptures & Old Books
    with tab6:
        st.header("📚 Add Scriptures & Old Books")

        option = st.radio("Choose source:", ["Project Gutenberg", "Internet Archive", "Upload Local Text"])

        if option == "Project Gutenberg":
            query = st.text_input("Enter book/scripture name", placeholder="e.g., Bhagavad Gita, Bible, Mahabharata")
            if st.button("📖 Fetch from Gutenberg"):
                books = services['corpus'].fetch_from_gutenberg(query)
                if books:
                    st.success(f"Fetched {len(books)} books from Project Gutenberg")
                    for book in books:
                        st.write(f"### {book['title']}")
                        st.write(book['content'][:1000] + "...")
                        # Add embeddings
                        chunks = services['embeddings'].process_documents_for_embedding([book], 1000)
                        embeddings = services['embeddings'].generate_embeddings([c['content'] for c in chunks])
                        st.session_state.vector_store.add_documents(embeddings, chunks)
                else:
                    st.warning("No results found.")

        elif option == "Internet Archive":
            query = st.text_input("Enter book/scripture name", placeholder="e.g., Rigveda, Quran, Dead Sea Scrolls")
            if st.button("📖 Fetch from Internet Archive"):
                books = services['corpus'].fetch_from_archive(query)
                if books:
                    st.success(f"Fetched {len(books)} books from Internet Archive")
                    for book in books:
                        st.write(f"### {book['title']}")
                        st.write(book['content'][:1000] + "...")
                        chunks = services['embeddings'].process_documents_for_embedding([book], 1000)
                        embeddings = services['embeddings'].generate_embeddings([c['content'] for c in chunks])
                        st.session_state.vector_store.add_documents(embeddings, chunks)
                else:
                    st.warning("No results found.")

        elif option == "Upload Local Text":
            uploaded_file = st.file_uploader("Upload .txt file", type=["txt"])
            if uploaded_file and st.button("📖 Process Local File"):
                book = services['corpus'].load_local_text(uploaded_file)
                st.write(f"### {book['title']}")
                st.write(book['content'][:1000] + "...")
                chunks = services['embeddings'].process_documents_for_embedding([book], 1000)
                embeddings = services['embeddings'].generate_embeddings([c['content'] for c in chunks])
                st.session_state.vector_store.add_documents(embeddings, chunks)
                st.success("File processed and added to vector store.")

if __name__ == "__main__":
    main()