---

# 🎓 Language-Agnostic Campus Chatbot

**Team:** Stack Overflowers | **University:** Ganpat University – ICT
**Hackathon:** HackX 2025 – Smart Education Track

---

## 🌟 Overview

A **multilingual AI chatbot** powered by **RAG (Retrieval-Augmented Generation)** and **LLaMA 3.3**, built to assist students in **10 Indian languages** with queries about fees, exams, hostels, scholarships, placements, and more — using verified university FAQs and circulars.

---

## ⚙️ Key Features

* 🌐 **10 Languages:** English, Hindi, Gujarati, Marathi, Tamil, Telugu, Bengali, Kannada, Malayalam, Punjabi
* 🧠 **RAG Architecture:** Fact-grounded and context-aware responses
* 🔍 **Semantic Search:** Intelligent retrieval via ChromaDB
* 💬 **Conversation Memory:** Multi-turn dialogue handling
* 🧾 **Conversation Logging:** For analytics and improvement
* 🔑 **REST API Integration & Docker Support** for deployment
* 👨‍🏫 **Human Handoff:** Auto-escalation for uncertain queries

---

## 🏗️ Architecture

```
User → FastAPI → RAG Engine → ChromaDB → Groq API (LLaMA 3.3)
                             ↘ Translation (Google)
```

---

## 🛠️ Tech Stack

| Component       | Technology              |
| --------------- | ----------------------- |
| **LLM**         | LLaMA 3.3 (Groq API)    |
| **Framework**   | FastAPI + LangChain     |
| **Vector DB**   | ChromaDB                |
| **Embeddings**  | all-MiniLM-L6-v2        |
| **Translation** | Google Translate API    |
| **Language**    | Python 3.12+            |
| **Deployment**  | Docker + Docker Compose |

---

## 🚀 Quick Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/HackX_StackOverflowers.git
cd HackX_StackOverflowers/backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Add your GROQ_API_KEY inside .env

# Initialize database
python rag_engine.py

# Start server
python main.py
# Runs at http://localhost:8000
```

---

## 🔌 API Endpoints

| Endpoint                 | Method | Description           |
| ------------------------ | ------ | --------------------- |
| `/health`                | GET    | Server status         |
| `/languages`             | GET    | Supported languages   |
| `/chat`                  | POST   | Main chat endpoint    |
| `/conversations/{id}`    | GET    | Fetch session history |
| `/reload-knowledge-base` | POST   | Reload FAQs/circulars |

---

## 💬 Example Request

```json
POST /chat
{
  "query": "परीक्षा कब है?",
  "language": "hi",
  "session_id": "user123"
}
```

**Response:**
“परीक्षा 15 मार्च 2025 से शुरू होगी…”

---

## 🐳 Docker Deployment

```bash
docker-compose up --build -d
# or
docker run -p 8000:8000 -e GROQ_API_KEY=your_key campus-chatbot:latest
```

---

## 👥 Team Stack Overflowers

| Name            | Role                   | Contact                                                     |
| --------------- | ---------------------- | ----------------------------------------------------------- |
| Aryan Patel     | Backend Lead           | [aaryanpatel03@gmail.com](mailto:aaryanpatel03@gmail.com)   |
| Tirth Patel     | Frontend & Integration | [tirth554patel@gmail.com](mailto:tirth554patel@gmail.com)   |
| Krish Patel     | DevOps & Docker        | [krishpatel15@yahoo.com](mailto:krishpatel15@yahoo.com)     |
| Mrigaksh Dasani | Data & Documentation   | [mrigakshdasani@gmail.com](mailto:mrigakshdasani@gmail.com) |

---

## 🎯 Future Enhancements

* WhatsApp & voice integration
* User PDF upload
* Analytics dashboard
* ERP & mobile app integration

---

**Built with ❤️ by Stack Overflowers for HackX 2025**

---
