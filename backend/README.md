# Backend - Language Agnostic Chatbot

This directory contains the complete backend implementation for the multilingual campus chatbot.

## 📁 Directory Structure
```
backend/
├── main.py                 # FastAPI application
├── rag_engine.py          # RAG implementation
├── translation.py         # Translation service
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── .env.example          # Environment variables template
├── .env                  # Your API keys (not in git)
├── conversation_logs.json # Chat logs (generated)
├── data/
│   ├── faqs.json         # FAQ database
│   └── sample_circulars/ # University documents
├── chroma_db/            # Vector database (generated)
└── venv/                 # Virtual environment (not in git)
```

## 🚀 Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
nano .env  # Add your GROQ_API_KEY

# Initialize knowledge base
python rag_engine.py

# Start server
python main.py
```

Server runs at: http://localhost:8000

## 🧩 Components

### 1. RAG Engine (`rag_engine.py`)
- Document loading and chunking
- Vector embeddings with all-MiniLM-L6-v2
- ChromaDB for semantic search
- LLaMA 3.3 via Groq for generation
- Conversation memory management

### 2. Translation Service (`translation.py`)
- Automatic language detection
- Translation using Google Translate
- Caching for performance
- Support for 10 Indian languages

### 3. FastAPI Server (`main.py`)
- RESTful API endpoints
- Request/response validation
- CORS middleware
- Conversation logging
- Background tasks

## 🔑 Environment Variables

Create `.env` file with:
```env
GROQ_API_KEY=your_groq_api_key
API_HOST=0.0.0.0
API_PORT=8000
CHROMA_PERSIST_DIRECTORY=./chroma_db
LOG_LEVEL=INFO
```

## 📊 Data Management

### Adding FAQs

Edit `data/faqs.json`:
```json
{
  "id": "faq_new",
  "category": "Category",
  "question": "Question text?",
  "answer": "Answer text.",
  "keywords": ["keyword1", "keyword2"]
}
```

### Adding Circulars
```bash
# Copy documents to circulars folder
cp new_document.txt data/sample_circulars/

# Reload knowledge base
curl -X POST http://localhost:8000/reload-knowledge-base
```

## 🧪 Testing
```bash
# Test RAG engine
python rag_engine.py

# Test translation
python translation.py

# Test API (server must be running)
curl http://localhost:8000/health
```

## 📖 API Endpoints

- `GET /` - Root info
- `GET /health` - Health check
- `GET /languages` - Supported languages
- `POST /chat` - Main chat endpoint
- `GET /conversations/{id}` - Get history
- `DELETE /conversations/{id}` - Clear history
- `GET /logs` - View conversation logs
- `GET /stats` - Usage statistics
- `POST /reload-knowledge-base` - Reload documents

Full API docs: http://localhost:8000/docs

## 🐛 Common Issues

**Port already in use:**
```bash
# Use different port
API_PORT=8001 python main.py
```

**ChromaDB errors:**
```bash
# Delete and recreate
rm -rf chroma_db/
python rag_engine.py
```

**Translation errors:**
```bash
# Check internet connection
# Google Translate requires network access
```

## 📦 Dependencies

Major packages:
- `fastapi` - Web framework
- `langchain` - RAG orchestration
- `chromadb` - Vector database
- `groq` - LLM API client
- `googletrans` - Translation
- `sentence-transformers` - Embeddings
- `pypdf` - PDF processing

See `requirements.txt` for complete list.

## 🔒 Security

- API keys in `.env` (not committed)
- CORS configured
- Input validation on all endpoints
- No sensitive data in logs

## 📝 Logging

Logs are written to:
- Console (stdout)
- `conversation_logs.json` (conversation history)

Log format:
```
2025-01-31 10:30:00 - module - LEVEL - message
```

## 🚀 Deployment

### Local
```bash
python main.py
```

### Docker
```bash
docker build -t chatbot-backend .
docker run -p 8000:8000 -e GROQ_API_KEY=xxx chatbot-backend
```

### Production
- Use gunicorn with multiple workers
- Set up HTTPS with nginx
- Configure proper CORS origins
- Enable rate limiting
- Set up monitoring

---

For full documentation, see main [README.md](../README.md)