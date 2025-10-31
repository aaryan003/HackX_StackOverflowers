"""
FastAPI Server for Language Agnostic Campus Chatbot
Provides REST API endpoints for multilingual conversational AI
"""

import os
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import logging

# Import our custom modules
from rag_engine import RAGEngine
from translation import TranslationService

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances (will be initialized on startup)
rag_engine: Optional[RAGEngine] = None
translation_service: Optional[TranslationService] = None
conversation_logs: List[Dict[str, Any]] = []

# Conversation logs file
LOGS_FILE = "conversation_logs.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup: Initialize RAG engine and translation service
    logger.info("Starting up application...")
    
    global rag_engine, translation_service
    
    try:
        # Initialize RAG Engine
        logger.info("Initializing RAG Engine...")
        rag_engine = RAGEngine(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            data_dir="./data",
            chroma_persist_dir="./chroma_db"
        )
        
        # Create or load vector store
        rag_engine.create_vector_store(force_reload=False)
        logger.info("RAG Engine initialized successfully")
        
        # Initialize Translation Service
        logger.info("Initializing Translation Service...")
        translation_service = TranslationService(default_language='en')
        logger.info("Translation Service initialized successfully")
        
        # Load existing conversation logs
        load_conversation_logs()
        
        logger.info("Application startup complete!")
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown: Save conversation logs
    logger.info("Shutting down application...")
    save_conversation_logs()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Language Agnostic Campus Chatbot API",
    description="Multilingual conversational AI for Ganpat University",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# PYDANTIC MODELS (Request/Response Schemas)
# ============================================================================

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    query: str = Field(..., description="User's question/query", min_length=1)
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")
    language: Optional[str] = Field(None, description="Preferred response language (auto-detect if None)")
    user_id: Optional[str] = Field(None, description="User identifier")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "मुझे छात्रवृत्ति के बारे में बताओ",
                "session_id": "user_123_session_1",
                "language": "hi",
                "user_id": "user_123"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    session_id: str
    original_query: str
    detected_language: str
    language_name: str
    english_query: str
    response: str
    english_response: str
    confidence: float
    needs_human_handoff: bool
    sources: List[Dict[str, str]]
    timestamp: str
    conversation_id: str


class ConversationHistory(BaseModel):
    """Model for conversation history"""
    session_id: str
    messages: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    rag_engine_ready: bool
    translation_service_ready: bool
    total_conversations: int


class SupportedLanguagesResponse(BaseModel):
    """Supported languages response"""
    languages: Dict[str, str]
    total: int


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_conversation_logs():
    """Load conversation logs from file"""
    global conversation_logs
    
    if os.path.exists(LOGS_FILE):
        try:
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                conversation_logs = json.load(f)
            logger.info(f"Loaded {len(conversation_logs)} conversation logs")
        except Exception as e:
            logger.error(f"Error loading conversation logs: {str(e)}")
            conversation_logs = []
    else:
        conversation_logs = []
        logger.info("No existing conversation logs found, starting fresh")


def save_conversation_logs():
    """Save conversation logs to file"""
    try:
        with open(LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(conversation_logs, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(conversation_logs)} conversation logs")
    except Exception as e:
        logger.error(f"Error saving conversation logs: {str(e)}")


def log_conversation(conversation_data: Dict[str, Any]):
    """Add conversation to logs"""
    conversation_logs.append(conversation_data)
    
    # Keep only last 1000 conversations in memory
    if len(conversation_logs) > 1000:
        conversation_logs.pop(0)
    
    # Save to file in background
    save_conversation_logs()


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Language Agnostic Campus Chatbot API",
        "version": "1.0.0",
        "university": "Ganpat University",
        "team": "Stack Overflowers",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns system status and readiness
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "rag_engine_ready": rag_engine is not None,
        "translation_service_ready": translation_service is not None,
        "total_conversations": len(conversation_logs)
    }


@app.get("/languages", response_model=SupportedLanguagesResponse, tags=["Languages"])
async def get_supported_languages():
    """
    Get list of supported languages
    """
    if not translation_service:
        raise HTTPException(status_code=503, detail="Translation service not ready")
    
    languages = translation_service.get_supported_languages()
    
    return {
        "languages": languages,
        "total": len(languages)
    }


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Main chat endpoint - handles multilingual queries
    
    Flow:
    1. Detect user's language
    2. Translate query to English
    3. Perform RAG (semantic search + generation)
    4. Translate response back to user's language
    5. Log conversation
    """
    
    # Validate services are ready
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not ready")
    if not translation_service:
        raise HTTPException(status_code=503, detail="Translation service not ready")
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"
        conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"Processing chat request - Session: {session_id}")
        
        # Step 1 & 2: Translate query to English
        translation_result = translation_service.translate_query_response(
            user_query=request.query,
            bot_response="",  # Will be filled after RAG
            target_language=request.language
        )
        
        english_query = translation_result['english_query']
        detected_language = translation_result['detected_language']
        language_name = translation_result['language_name']
        
        logger.info(f"Query translated: {detected_language} -> en")
        
        # Step 3: RAG - Get response from knowledge base
        rag_result = rag_engine.query(
            user_query=english_query,
            session_id=session_id,
            k=3
        )
        
        english_response = rag_result['response']
        confidence = rag_result['confidence']
        needs_handoff = rag_result['needs_human_handoff']
        sources = rag_result['sources']
        
        logger.info(f"RAG response generated - Confidence: {confidence:.2f}")
        
        # Step 4: Translate response back to user's language
        response_language = request.language or detected_language
        
        if response_language != 'en':
            translated_response, _ = translation_service.translate(
                text=english_response,
                src_lang='en',
                dest_lang=response_language
            )
        else:
            translated_response = english_response
        
        logger.info(f"Response translated: en -> {response_language}")
        
        # Prepare response
        response_data = {
            "session_id": session_id,
            "original_query": request.query,
            "detected_language": detected_language,
            "language_name": language_name,
            "english_query": english_query,
            "response": translated_response,
            "english_response": english_response,
            "confidence": confidence,
            "needs_human_handoff": needs_handoff,
            "sources": sources,
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conversation_id
        }
        
        # Step 5: Log conversation (in background)
        log_data = {
            **response_data,
            "user_id": request.user_id
        }
        background_tasks.add_task(log_conversation, log_data)
        
        logger.info(f"Chat request completed - Conversation ID: {conversation_id}")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@app.get("/conversations/{session_id}", response_model=ConversationHistory, tags=["Conversations"])
async def get_conversation_history(session_id: str, limit: int = 10):
    """
    Get conversation history for a session
    """
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not ready")
    
    # Get from RAG engine's memory
    history = rag_engine.conversation_memory.get(session_id, [])
    
    # Limit results
    limited_history = history[-limit:] if len(history) > limit else history
    
    return {
        "session_id": session_id,
        "messages": limited_history
    }


@app.delete("/conversations/{session_id}", tags=["Conversations"])
async def clear_conversation(session_id: str):
    """
    Clear conversation history for a session
    """
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not ready")
    
    rag_engine.clear_conversation(session_id)
    
    return {
        "message": f"Conversation history cleared for session: {session_id}",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/logs", tags=["Admin"])
async def get_conversation_logs(limit: int = 50, language: Optional[str] = None):
    """
    Get conversation logs (admin endpoint)
    Optionally filter by language
    """
    filtered_logs = conversation_logs
    
    # Filter by language if specified
    if language:
        filtered_logs = [
            log for log in conversation_logs 
            if log.get('detected_language') == language
        ]
    
    # Return last N logs
    return {
        "total": len(filtered_logs),
        "showing": min(limit, len(filtered_logs)),
        "logs": filtered_logs[-limit:] if filtered_logs else []
    }


@app.get("/stats", tags=["Admin"])
async def get_statistics():
    """
    Get usage statistics
    """
    if not conversation_logs:
        return {
            "total_conversations": 0,
            "languages_used": {},
            "average_confidence": 0.0,
            "handoff_rate": 0.0
        }
    
    # Calculate statistics
    language_counts = {}
    total_confidence = 0.0
    handoff_count = 0
    
    for log in conversation_logs:
        lang = log.get('detected_language', 'unknown')
        language_counts[lang] = language_counts.get(lang, 0) + 1
        total_confidence += log.get('confidence', 0.0)
        if log.get('needs_human_handoff', False):
            handoff_count += 1
    
    total = len(conversation_logs)
    
    return {
        "total_conversations": total,
        "languages_used": language_counts,
        "average_confidence": round(total_confidence / total, 2) if total > 0 else 0.0,
        "handoff_rate": round((handoff_count / total) * 100, 2) if total > 0 else 0.0,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/reload-knowledge-base", tags=["Admin"])
async def reload_knowledge_base():
    """
    Reload knowledge base (admin endpoint)
    Useful when new documents are added
    """
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not ready")
    
    try:
        logger.info("Reloading knowledge base...")
        rag_engine.create_vector_store(force_reload=True)
        logger.info("Knowledge base reloaded successfully")
        
        return {
            "message": "Knowledge base reloaded successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error reloading knowledge base: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reloading knowledge base: {str(e)}"
        )


# ============================================================================
# MAIN (for local testing)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True,
        log_level="info"
    )