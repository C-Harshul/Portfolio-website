# Portfolio Website

A personal portfolio website with an AI-powered chat interface that allows visitors to learn about Harshul Chandrashekhar's experience, projects, and background.

## Project Structure

```
Portfolio-Website/
├── frontend/              # Frontend files
│   ├── index.html        # Main HTML file
│   ├── styles.css        # CSS styles
│   ├── app.js            # JavaScript application logic
│   └── assets/           # Static assets (images, etc.)
│       └── IMG_8523.PNG  # Profile picture
│
├── backend/              # Backend server
│   └── server.py         # Flask server and API endpoints
│
├── rag/                  # RAG (Retrieval-Augmented Generation) modules
│   ├── chain.py          # RAG chain builder
│   ├── prompt.py         # Prompt templates
│   ├── retriever.py      # Document retrieval logic
│   └── vectorstore.py    # Vector store management
│
├── ingestion/            # Document ingestion modules
│   ├── embeddings.py     # Embedding models
│   ├── pdf_loader.py     # PDF loading and chunking
│   └── ingest.py         # Ingestion pipeline
│
├── config/               # Configuration
│   └── settings.py      # Environment settings
│
└── data/                 # Data storage
    └── chroma/           # ChromaDB vector database
```

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   Create a `.env` file with:
   ```bash
   GOOGLE_API_KEY=your_google_api_key
   CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
   CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
   LANGCHAIN_API_KEY=your_langchain_api_key
   LANGCHAIN_PROJECT=profile-website
   ```

3. **Run the Server**
   ```bash
   python backend/server.py
   ```
   
   Or use the run script:
   ```bash
   ./run.sh
   ```

4. **Access the Website**
   Open your browser and go to: `http://localhost:5001`

## Features

- **Clean Chat Interface**: Minimalist design with smooth animations
- **AI-Powered Responses**: Uses RAG (Retrieval-Augmented Generation) with Google Gemini
- **Vector Search**: ChromaDB for efficient document retrieval
- **Personal Branding**: Profile picture and personalized experience

## Development

- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Backend**: Flask (Python)
- **AI/ML**: LangChain, Google Gemini, Cloudflare Workers AI
- **Vector DB**: ChromaDB

## API Endpoints

- `GET /` - Serves the main HTML page
- `GET /<path>` - Serves static files (CSS, JS, images)
- `POST /api/chat` - Chat API endpoint
  - Request: `{ "message": "user message" }`
  - Response: `{ "response": "assistant reply" }`
