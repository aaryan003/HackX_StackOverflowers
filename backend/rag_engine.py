"""
RAG Engine for Language Agnostic Chatbot
Handles document ingestion, embedding, semantic search, and response generation
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Groq LLM
from groq import Groq

# Document loaders
from langchain_community.document_loaders import TextLoader, DirectoryLoader

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Retrieval-Augmented Generation Engine for Campus Chatbot
    """
    
    def __init__(
        self,
        groq_api_key: str,
        data_dir: str = "./data",
        chroma_persist_dir: str = "./chroma_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize RAG Engine
        
        Args:
            groq_api_key: API key for Groq (LLaMA3)
            data_dir: Directory containing FAQs and circulars
            chroma_persist_dir: Directory to persist vector database
            embedding_model: HuggingFace embedding model name
        """
        self.groq_api_key = groq_api_key
        self.data_dir = data_dir
        self.chroma_persist_dir = chroma_persist_dir
        self.embedding_model_name = embedding_model
        
        # Initialize Groq client
        self.groq_client = Groq(api_key=groq_api_key)
        
        # Initialize embeddings
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Vector store
        self.vectorstore = None
        
        # Conversation memory
        self.conversation_memory = {}
        
        logger.info("RAG Engine initialized successfully")
    
    
    def load_documents(self) -> List[Document]:
        """
        Load all documents (FAQs and circulars) from data directory
        
        Returns:
            List of LangChain Document objects
        """
        documents = []
        
        # Load FAQs
        faq_path = os.path.join(self.data_dir, "faqs.json")
        if os.path.exists(faq_path):
            logger.info(f"Loading FAQs from {faq_path}")
            with open(faq_path, 'r', encoding='utf-8') as f:
                faq_data = json.load(f)
                
            for faq in faq_data.get('faqs', []):
                content = f"""
Question: {faq['question']}
Answer: {faq['answer']}
Category: {faq['category']}
Keywords: {', '.join(faq['keywords'])}
"""
                doc = Document(
                    page_content=content,
                    metadata={
                        'source': 'FAQ',
                        'faq_id': faq['id'],
                        'category': faq['category'],
                        'type': 'faq'
                    }
                )
                documents.append(doc)
            
            logger.info(f"Loaded {len(faq_data.get('faqs', []))} FAQs")
        
        # Load circulars (text files)
        circulars_dir = os.path.join(self.data_dir, "sample_circulars")
        if os.path.exists(circulars_dir):
            logger.info(f"Loading circulars from {circulars_dir}")
            
            loader = DirectoryLoader(
                circulars_dir,
                glob="**/*.txt",
                loader_cls=TextLoader,
                loader_kwargs={'encoding': 'utf-8'}
            )
            circular_docs = loader.load()
            
            # Add metadata
            for doc in circular_docs:
                doc.metadata['source'] = 'Circular'
                doc.metadata['type'] = 'circular'
                doc.metadata['filename'] = os.path.basename(doc.metadata.get('source', ''))
            
            documents.extend(circular_docs)
            logger.info(f"Loaded {len(circular_docs)} circulars")
        
        logger.info(f"Total documents loaded: {len(documents)}")
        return documents
    
    
    def create_vector_store(self, force_reload: bool = False):
        """
        Create or load vector store from documents
        
        Args:
            force_reload: If True, recreate vector store from scratch
        """
        # Check if vector store already exists
        if os.path.exists(self.chroma_persist_dir) and not force_reload:
            logger.info("Loading existing vector store...")
            self.vectorstore = Chroma(
                persist_directory=self.chroma_persist_dir,
                embedding_function=self.embeddings
            )
            logger.info("Vector store loaded successfully")
            return
        
        # Load documents
        documents = self.load_documents()
        
        if not documents:
            raise ValueError("No documents found to create vector store")
        
        # Split documents into chunks
        logger.info("Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        splits = text_splitter.split_documents(documents)
        logger.info(f"Created {len(splits)} document chunks")
        
        # Create vector store
        logger.info("Creating vector store with embeddings...")
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.chroma_persist_dir
        )
        
        # Persist to disk
        self.vectorstore.persist()
        logger.info("Vector store created and persisted successfully")
    
    
    def semantic_search(
        self,
        query: str,
        k: int = 3,
        filter_dict: Optional[Dict] = None
    ) -> List[Tuple[Document, float]]:
        """
        Perform semantic search on vector store
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Metadata filter
            
        Returns:
            List of (Document, score) tuples
        """
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Call create_vector_store() first")
        
        logger.info(f"Searching for: {query}")
        
        results = self.vectorstore.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter_dict
        )
        
        logger.info(f"Found {len(results)} relevant documents")
        return results
    
    
    def generate_response(
        self,
        query: str,
        context_docs: List[Document],
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate response using Groq LLaMA3 with retrieved context
        
        Args:
            query: User query
            context_docs: Retrieved documents for context
            conversation_history: Previous conversation turns
            
        Returns:
            Dictionary with response and metadata
        """
        # Prepare context from retrieved documents
        context = "\n\n".join([
            f"[Source: {doc.metadata.get('source', 'Unknown')} - {doc.metadata.get('category', 'General')}]\n{doc.page_content}"
            for doc in context_docs
        ])
        
        # Prepare conversation history
        history_text = ""
        if conversation_history:
            for turn in conversation_history[-3:]:  # Last 3 turns
                history_text += f"User: {turn.get('user', '')}\nAssistant: {turn.get('assistant', '')}\n\n"
        
        # Create prompt
        prompt = f"""You are a helpful campus assistant chatbot for Ganpat University. Your role is to provide accurate, friendly, and concise information to students.

Previous Conversation:
{history_text if history_text else "None"}

Relevant Information from University Database:
{context}

Current Student Query: {query}

Instructions:
1. Answer based ONLY on the provided information above
2. Be friendly, helpful, and concise
3. If the information is not in the context, politely say you don't have that information and suggest contacting the relevant department
4. Include specific details like dates, fees, deadlines when available
5. If asked about processes, break them down into clear steps
6. For contact information, provide it if available in the context

Answer:"""

        try:
            # Call Groq API
            logger.info("Generating response with Groq LLaMA3...")
            
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful and knowledgeable campus assistant for Ganpat University. Provide accurate, friendly responses based on the given context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile",  # Using LLaMA 3.1 70B for better quality
                temperature=0.3,  # Low temperature for factual responses
                max_tokens=500,
                top_p=0.9,
            )
            
            response_text = chat_completion.choices[0].message.content
            
            # Calculate confidence based on context relevance
            confidence = self._calculate_confidence(context_docs)
            
            return {
                "response": response_text,
                "confidence": confidence,
                "sources": [
                    {
                        "type": doc.metadata.get('type', 'unknown'),
                        "category": doc.metadata.get('category', 'General'),
                        "source": doc.metadata.get('source', 'Unknown')
                    }
                    for doc in context_docs
                ],
                "needs_human_handoff": confidence < 0.5,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "response": "I apologize, but I'm having trouble generating a response right now. Please try again or contact the university office for assistance.",
                "confidence": 0.0,
                "sources": [],
                "needs_human_handoff": True,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    
    def _calculate_confidence(self, docs: List[Document]) -> float:
        """
        Calculate confidence score based on retrieved documents
        
        Args:
            docs: Retrieved documents
            
        Returns:
            Confidence score between 0 and 1
        """
        if not docs:
            return 0.0
        
        # Simple heuristic: confidence based on number and type of sources
        score = 0.5  # Base score
        
        # Bonus for multiple sources
        if len(docs) >= 2:
            score += 0.2
        
        # Bonus for FAQ sources (usually more direct)
        faq_count = sum(1 for doc in docs if doc.metadata.get('type') == 'faq')
        if faq_count > 0:
            score += 0.2
        
        # Bonus for official circulars
        circular_count = sum(1 for doc in docs if doc.metadata.get('type') == 'circular')
        if circular_count > 0:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    
    def query(
        self,
        user_query: str,
        session_id: str = "default",
        k: int = 3
    ) -> Dict[str, Any]:
        """
        Main query method - performs RAG pipeline
        
        Args:
            user_query: User's question
            session_id: Session identifier for conversation tracking
            k: Number of documents to retrieve
            
        Returns:
            Response dictionary with answer and metadata
        """
        logger.info(f"Processing query: {user_query}")
        
        # Retrieve relevant documents
        search_results = self.semantic_search(query=user_query, k=k)
        context_docs = [doc for doc, score in search_results]
        
        # Get conversation history for this session
        conversation_history = self.conversation_memory.get(session_id, [])
        
        # Generate response
        result = self.generate_response(
            query=user_query,
            context_docs=context_docs,
            conversation_history=conversation_history
        )
        
        # Update conversation memory
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = []
        
        self.conversation_memory[session_id].append({
            "user": user_query,
            "assistant": result["response"],
            "timestamp": result["timestamp"]
        })
        
        # Keep only last 10 turns
        self.conversation_memory[session_id] = self.conversation_memory[session_id][-10:]
        
        return result
    
    
    def clear_conversation(self, session_id: str = "default"):
        """Clear conversation history for a session"""
        if session_id in self.conversation_memory:
            del self.conversation_memory[session_id]
            logger.info(f"Cleared conversation history for session: {session_id}")


# Utility function for testing
def test_rag_engine():
    """Test the RAG engine with sample queries"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize engine
    engine = RAGEngine(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        data_dir="./data",
        chroma_persist_dir="./chroma_db"
    )
    
    # Create vector store
    print("Creating vector store...")
    engine.create_vector_store(force_reload=True)
    
    # Test queries
    test_queries = [
        "What is the fee payment deadline?",
        "How do I apply for scholarship?",
        "Tell me about hostel facilities"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        result = engine.query(query)
        
        print(f"\nResponse: {result['response']}")
        print(f"\nConfidence: {result['confidence']:.2f}")
        print(f"Sources: {result['sources']}")
        print(f"Needs Human: {result['needs_human_handoff']}")


if __name__ == "__main__":
    test_rag_engine()