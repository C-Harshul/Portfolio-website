# GST RAG System

A LangChain-based Retrieval-Augmented Generation (RAG) system for GST (Goods and Services Tax) regulation queries. This system ingests GST regulation PDFs and provides accurate, context-based answers using Google Gemini and Cloudflare Workers AI.

## Features

- **PDF Ingestion**: Automated processing of GST regulation PDFs with chunking
- **Vector Storage**: ChromaDB-based vector storage with batch processing
- **Modern Embeddings**: Cloudflare Workers AI embeddings (BGE-base-en-v1.5)
- **Advanced LLM**: Google Gemini 2.5 Flash for response generation
- **LangChain Integration**: Full LangChain LCEL pipeline (Retriever → Prompt → LLM → Parser)
- **Streamlit Frontend**: User-friendly web interface with examples
- **Robust Processing**: Safe document ingestion with error handling

## Project Structure

```
gst-rag/
├── ingestion/
│   ├── email_listener.py        # Email attachment processing (optional)
│   ├── s3_trigger_lambda.py     # AWS Lambda S3 trigger handler
│   ├── pdf_loader.py            # PDF loading and chunking
│   ├── embeddings.py            # Swappable embedding models
│   └── ingest.py                # End-to-end ingestion pipeline
├── rag/
│   ├── vectorstore.py           # ChromaDB vector store management
│   ├── retriever.py             # Document retrieval logic
│   └── prompt.py                # RAG prompt templates
├── app/
│   └── app.py                   # Streamlit web application
├── config/
│   └── settings.py              # Configuration and environment handling
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. **Clone and Install Dependencies**
   ```bash
   git clone <repository-url>
   cd gst-rag
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   The `.env` file should contain:
   ```bash
   GOOGLE_API_KEY=your_google_api_key
   CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
   CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
   ```

3. **Required API Keys**
   - **Google AI API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **Cloudflare Account ID & API Token**: Get from [Cloudflare Dashboard](https://dash.cloudflare.com/)

## Usage

### 1. Ingest GST Documents
```bash
# Ingest a single PDF
python ingest_documents.py documents/gst_rules.pdf

# Ingest all PDFs from a directory
python ingest_documents.py documents/
```

### 2. Run the Streamlit App
```bash
streamlit run app/app.py
```

### 3. Query the System
- Open the web interface at `http://localhost:8501`
- Ask GST-related questions like:
  - "What is the GST rate for restaurant services?"
  - "What are the input tax credit rules?"
  - "What is the threshold for GST registration?"

## Architecture

The system uses a modern LangChain LCEL (LangChain Expression Language) pipeline:

```
User Query → Retriever → Prompt Template → Google Gemini → Response
```

### Components:
1. **PDF Ingestion**: `pypdf` + chunking with overlap
2. **Embeddings**: Cloudflare Workers AI (BGE-base-en-v1.5, 768-dim)
3. **Vector Store**: ChromaDB with persistence
4. **LLM**: Google Gemini 2.5 Flash
5. **Frontend**: Streamlit with caching

### LangChain Integration:
```python
# The RAG chain in rag/chain.py
chain = (
    {
        "context": retriever,
        "question": RunnablePassthrough()
    }
    | RAG_PROMPT
    | llm
    | StrOutputParser()
)
```

## Development

This is a starter project with minimal implementations. Each module contains placeholder functions ready for business logic implementation.

## License

[Add your license information here]