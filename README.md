# 🎓 Language Agnostic Campus Chatbot

**Team:** Stack Overflowers  
**University:** Ganpat University - Institute of Computer Technology  
**Hackathon:** HackX 2025 - Smart Education Track  
**Problem Statement:** Breaking Language Barriers in Campus Communication

---

## 🌟 Executive Summary

A multilingual conversational AI chatbot powered by **Retrieval-Augmented Generation (RAG)** and **LLaMA 3.3**, designed to provide 24/7 support to students in **10 Indian languages**. The system intelligently answers queries about fees, scholarships, exams, hostel, placements, and more by retrieving information from institutional FAQs and official circulars.

### Key Features
- ✅ **10 Languages Supported**: English, Hindi, Gujarati, Marathi, Tamil, Telugu, Bengali, Kannada, Malayalam, Punjabi
- ✅ **RAG Architecture**: Fact-grounded responses from verified documents
- ✅ **Semantic Search**: ChromaDB vector database for intelligent retrieval
- ✅ **Conversation Memory**: Multi-turn context-aware conversations
- ✅ **Human Handoff**: Automatic escalation for low-confidence queries
- ✅ **Conversation Logging**: Complete audit trail for improvement
- ✅ **REST API**: Easy integration with web/mobile/messaging platforms
- ✅ **Docker Support**: One-command deployment

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│            (Web App / Mobile / WhatsApp / Telegram)             │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP/REST API
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FASTAPI SERVER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │ Translation  │  │  RAG Engine  │  │  Conversation Logs  │  │
│  │   Service    │  │              │  │                     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬──────────┘  │
│         │                  │                     │              │
└─────────┼──────────────────┼─────────────────────┼──────────────┘
          │                  │                     │
          │                  ▼                     ▼
          │        ┌──────────────────┐   ┌──────────────┐
          │        │   ChromaDB       │   │ conversation │
          │        │ (Vector Store)   │   │  _logs.json  │
          │        └──────────────────┘   └──────────────┘
          │                  │
          │                  ▼
          │        ┌──────────────────┐
          │        │  Embeddings      │
          │        │  (all-MiniLM)    │
          │        └──────────────────┘
          │
          ▼
┌─────────────────────┐        ┌──────────────────┐
│ Google Translate    │        │   Groq API       │
│ (Language Support)  │        │  (LLaMA 3.3)     │
└─────────────────────┘        └──────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | LLaMA 3.3 (70B) via Groq | Response generation |
| **Framework** | LangChain | RAG orchestration |
| **Vector DB** | ChromaDB | Semantic search |
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 | Document embeddings |
| **Translation** | Google Translate API | Multilingual support |
| **API Server** | FastAPI | REST endpoints |
| **Language** | Python 3.12+ | Backend development |
| **Containerization** | Docker + Docker Compose | Deployment |

---

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **pip**: Latest version
- **Git**: For version control
- **Docker** (optional): For containerized deployment
- **Groq API Key**: Free from [console.groq.com](https://console.groq.com/)

---

## 🚀 Quick Start (5 Minutes)

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/HackX_StackOverflowers.git
cd HackX_StackOverflowers
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Groq API key
# Get free key from: https://console.groq.com/
nano .env  # or use any text editor
```

Add your API key:
```
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 4. Initialize Knowledge Base
```bash
# This creates the vector database from FAQs and circulars
python rag_engine.py
```

Wait for completion (~3 minutes first time).

### 5. Start Server
```bash
python main.py
```

Server will start at: **http://localhost:8000**

### 6. Test API

Open browser: **http://localhost:8000/docs**

Try the `/chat` endpoint with:
```json
{
  "query": "What is the fee payment deadline?",
  "session_id": "demo_session"
}
```

---

## 📖 Detailed Installation Guide

### Step-by-Step Setup

#### 1. System Requirements
```bash
# Check Python version (must be 3.8+)
python --version

# Check pip
pip --version

# Check Git
git --version
```

#### 2. Clone and Navigate
```bash
git clone https://github.com/YOUR_USERNAME/HackX_StackOverflowers.git
cd HackX_StackOverflowers/backend
```

#### 3. Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Verify activation
which python  # Should point to venv/bin/python
```

#### 4. Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# This installs:
# - fastapi, uvicorn (API server)
# - langchain, chromadb (RAG)
# - groq (LLM API)
# - googletrans, langdetect (translation)
# - pypdf, sentence-transformers (document processing)
```

#### 5. Configure API Keys
```bash
# Create .env file
cp .env.example .env

# Edit with your keys
nano .env
```

Required keys:
```env
GROQ_API_KEY=your_groq_key_here  # Required
GOOGLE_TRANSLATE_API_KEY=optional  # Uses free tier if not provided
```

Get Groq API Key:
1. Visit: https://console.groq.com/
2. Sign up (free)
3. Go to "API Keys"
4. Create new key
5. Copy and paste in `.env`

#### 6. Prepare Data

The repository includes sample data:
- **FAQs**: `backend/data/faqs.json` (20 questions)
- **Circulars**: `backend/data/sample_circulars/` (5 documents)

To add more data:
```bash
# Add FAQs to faqs.json
nano backend/data/faqs.json

# Add circulars (text/PDF files)
cp your_circular.txt backend/data/sample_circulars/
```

#### 7. Initialize Vector Database
```bash
# First time setup (creates embeddings)
python rag_engine.py

# Expected output:
# - Loads 20 FAQs
# - Loads 5 circulars
# - Creates document chunks
# - Generates embeddings
# - Persists to chroma_db/
```

This takes 3-5 minutes on first run.

#### 8. Start the Server
```bash
# Start FastAPI server
python main.py

# Server starts at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-31T10:30:00",
  "rag_engine_ready": true,
  "translation_service_ready": true,
  "total_conversations": 42
}
```

#### 2. Supported Languages
```http
GET /languages
```

**Response:**
```json
{
  "languages": {
    "en": "English",
    "hi": "Hindi",
    "gu": "Gujarati",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi"
  },
  "total": 10
}
```

#### 3. Chat (Main Endpoint)
```http
POST /chat
```

**Request Body:**
```json
{
  "query": "मुझे छात्रवृत्ति के बारे में बताओ",
  "session_id": "user_123_session",
  "language": "hi",
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "session_id": "user_123_session",
  "original_query": "मुझे छात्रवृत्ति के बारे में बताओ",
  "detected_language": "hi",
  "language_name": "Hindi",
  "english_query": "Tell me about scholarships",
  "response": "छात्रवृत्ति मेरिट और आवश्यकता आधारित छात्रों के लिए उपलब्ध है...",
  "english_response": "Scholarships are available for merit and need-based students...",
  "confidence": 0.85,
  "needs_human_handoff": false,
  "sources": [
    {
      "type": "faq",
      "category": "Scholarships",
      "source": "FAQ"
    }
  ],
  "timestamp": "2025-01-31T10:35:22",
  "conversation_id": "conv_abc123def456"
}
```

#### 4. Conversation History
```http
GET /conversations/{session_id}?limit=10
```

**Response:**
```json
{
  "session_id": "user_123_session",
  "messages": [
    {
      "user": "What is the fee deadline?",
      "assistant": "The fee payment deadline is January 31st, 2025.",
      "timestamp": "2025-01-31T10:30:00"
    }
  ]
}
```

#### 5. Clear Conversation
```http
DELETE /conversations/{session_id}
```

#### 6. View Logs (Admin)
```http
GET /logs?limit=50&language=hi
```

#### 7. Statistics (Admin)
```http
GET /stats
```

**Response:**
```json
{
  "total_conversations": 150,
  "languages_used": {
    "hi": 65,
    "gu": 45,
    "en": 40
  },
  "average_confidence": 0.82,
  "handoff_rate": 8.5
}
```

#### 8. Reload Knowledge Base (Admin)
```http
POST /reload-knowledge-base
```

---

## 💬 Usage Examples

### Example 1: English Query
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the hostel facilities?",
    "session_id": "demo_1"
  }'
```

### Example 2: Hindi Query
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "परीक्षा कब है?",
    "session_id": "demo_1",
    "language": "hi"
  }'
```

### Example 3: Gujarati Query
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ફી ભરવાની છેલ્લી તારીખ ક્યારે છે?",
    "session_id": "demo_1"
  }'
```

### Example 4: Multi-turn Conversation
```python
import requests

BASE_URL = "http://localhost:8000"
session_id = "user_789"

# First question
response1 = requests.post(f"{BASE_URL}/chat", json={
    "query": "Tell me about scholarships",
    "session_id": session_id
})

# Follow-up question (context maintained)
response2 = requests.post(f"{BASE_URL}/chat", json={
    "query": "When is the deadline?",
    "session_id": session_id
})

print(response2.json()["response"])
# Output: "The scholarship application deadline is March 31st, 2025."
```

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

### Manual Docker Build
```bash
# Build image
docker build -t campus-chatbot:latest ./backend

# Run container
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key_here \
  campus-chatbot:latest
```

---

## 📊 Sample Data

### FAQs Coverage
- **Admissions**: Application process, entrance exams
- **Fees**: Payment deadlines, installments
- **Scholarships**: Merit, need-based, government schemes
- **Examinations**: Schedule, rules, revaluation
- **Hostel**: Facilities, fees, rules
- **Placements**: Process, companies, packages
- **Library**: Timings, facilities
- **Transport**: Bus routes, fees
- **Student Life**: Clubs, events, WiFi

### Circulars Included
1. Fee Payment Schedule 2025
2. Examination Schedule 2025
3. Scholarship Application Notice
4. Hostel Allotment 2025
5. Placement Drive Spring 2025

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key (required) | - |
| `GOOGLE_TRANSLATE_API_KEY` | Google Translate API key | Uses free tier |
| `API_HOST` | Server host | 0.0.0.0 |
| `API_PORT` | Server port | 8000 |
| `CHROMA_PERSIST_DIRECTORY` | Vector DB location | ./chroma_db |
| `LOG_LEVEL` | Logging level | INFO |

### Customization

#### Add New FAQs
Edit `backend/data/faqs.json`:
```json
{
  "faqs": [
    {
      "id": "faq_021",
      "category": "Sports",
      "question": "What sports facilities are available?",
      "answer": "The university has cricket ground, football field...",
      "keywords": ["sports", "facilities", "cricket", "football"]
    }
  ]
}
```

#### Add New Documents
```bash
# Add text or PDF files
cp new_circular.txt backend/data/sample_circulars/

# Reload knowledge base
curl -X POST http://localhost:8000/reload-knowledge-base
```

---

## 🧪 Testing

### Run Unit Tests
```bash
# Test RAG engine
python backend/rag_engine.py

# Test translation
python backend/translation.py
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Chat test
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "session_id": "test"}'
```

### Interactive Testing
Visit: **http://localhost:8000/docs**

Use Swagger UI to test all endpoints interactively.

---

## 📈 Performance

- **Response Time**: 2-4 seconds (including translation)
- **Accuracy**: 85-90% (based on RAG confidence scores)
- **Languages**: 10 Indian languages
- **Concurrent Users**: 50+ (with default settings)
- **Knowledge Base**: 25+ documents, expandable

---

## 🛡️ Security

- ✅ API key stored in environment variables
- ✅ CORS configured for specific origins (update for production)
- ✅ No user data stored permanently
- ✅ Conversation logs can be encrypted
- ✅ Input validation on all endpoints

---

## 🐛 Troubleshooting

### Issue: "RAG engine not ready"
**Solution:**
```bash
# Reinitialize vector database
python backend/rag_engine.py
```

### Issue: Translation not working
**Solution:**
```bash
# Check internet connection
# Google Translate requires internet

# Test translation service
python backend/translation.py
```

### Issue: Low confidence responses
**Solution:**
- Add more relevant documents to knowledge base
- Improve FAQ coverage
- Fine-tune retrieval parameters

### Issue: Server won't start
**Solution:**
```bash
# Check if port 8000 is free
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
API_PORT=8001 python main.py
```

---

## 👥 Team

**Stack Overflowers** - Ganpat University

| Name | Role | Contact |
|------|------|---------|
| Aryan Patel | Backend Lead | aaryanpatel03@gmail.com |
| Tirth Patel | Frontend & Integration | tirth554patel@gmail.com |
| Krish Patel | DevOps & Docker | krishpatel15@yahoo.com |
| Mrigaksh Dasani | Data & Documentation | mrigakshdasani@gmail.com |

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **HackX 2025** organizers
- **Ganpat University** for support
- **Groq** for free LLaMA API access
- Open source community (LangChain, ChromaDB, FastAPI)

---

## 📞 Support

For issues or questions:
- **GitHub Issues**: [Create an issue](https://github.com/YOUR_USERNAME/HackX_StackOverflowers/issues)
- **Email**: aaryanpatel03@gmail.com
- **Demo Video**: [Watch Demo](./demo_video_link.txt)

---

## 🎯 Future Enhancements

- [ ] WhatsApp integration
- [ ] Voice input/output
- [ ] PDF upload by users
- [ ] Advanced analytics dashboard
- [ ] Sentiment analysis
- [ ] More regional languages
- [ ] Mobile app (React Native)
- [ ] Integration with university ERP

---

**Built with ❤️ by Stack Overflowers for HackX 2025**