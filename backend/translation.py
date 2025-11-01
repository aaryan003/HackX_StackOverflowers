"""
Translation Layer for Multilingual Support
Handles language detection and translation for Indian languages
"""

import logging
from typing import Dict, Optional, Tuple
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
import time

# Set seed for consistent language detection
DetectorFactory.seed = 0

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranslationService:
    """
    Handles translation between English and regional languages
    """
    
    # Supported languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'hi': 'Hindi',
        'gu': 'Gujarati',
        'mr': 'Marathi',
        'ta': 'Tamil',
        'te': 'Telugu',
        'bn': 'Bengali',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'pa': 'Punjabi'
    }
    
    def __init__(self, default_language: str = 'en'):
        """
        Initialize Translation Service
        
        Args:
            default_language: Default language code (default: 'en')
        """
        self.default_language = default_language
        self.translation_cache = {}  # Simple cache to reduce API calls
        logger.info(f"Translation Service initialized with {len(self.SUPPORTED_LANGUAGES)} languages")
    
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of input text
        
        Args:
            text: Input text
            
        Returns:
            Language code (e.g., 'en', 'hi', 'gu')
        """
        try:
            detected = detect(text)
            
            # Map detected language to supported languages
            if detected in self.SUPPORTED_LANGUAGES:
                logger.info(f"Detected language: {self.SUPPORTED_LANGUAGES[detected]} ({detected})")
                return detected
            else:
                logger.warning(f"Unsupported language detected: {detected}, defaulting to {self.default_language}")
                return self.default_language
                
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}, defaulting to {self.default_language}")
            return self.default_language
    
    
    def translate(
        self,
        text: str,
        src_lang: Optional[str] = None,
        dest_lang: str = 'en',
        use_cache: bool = True
    ) -> Tuple[str, str]:
        """
        Translate text from source to destination language
        
        Args:
            text: Text to translate
            src_lang: Source language (auto-detect if None)
            dest_lang: Destination language code
            use_cache: Use cached translations if available
            
        Returns:
            Tuple of (translated_text, detected_source_language)
        """
        # Check cache first
        cache_key = f"{text}_{src_lang}_{dest_lang}"
        if use_cache and cache_key in self.translation_cache:
            logger.info("Using cached translation")
            return self.translation_cache[cache_key]
        
        try:
            # Auto-detect source language if not provided
            if src_lang is None:
                src_lang = self.detect_language(text)
            
            # Skip translation if source and destination are the same
            if src_lang == dest_lang:
                logger.info(f"Source and destination languages are same ({src_lang}), skipping translation")
                return text, src_lang
            
            # Perform translation
            logger.info(f"Translating from {src_lang} to {dest_lang}")
            
            # Add retry logic for API reliability
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    translator = GoogleTranslator(source=src_lang, target=dest_lang)
                    translated_text = translator.translate(text)
                    
                    logger.info(f"Translation successful (attempt {attempt + 1})")
                    
                    # Cache the result
                    if use_cache:
                        self.translation_cache[cache_key] = (translated_text, src_lang)
                    
                    return translated_text, src_lang
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Translation attempt {attempt + 1} failed: {str(e)}, retrying...")
                        time.sleep(1)  # Wait before retry
                    else:
                        raise e
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            # Fallback: return original text
            return text, src_lang or self.default_language
    
    
    def translate_query_response(
        self,
        user_query: str,
        bot_response: str,
        target_language: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Complete translation workflow for chatbot query-response
        
        Args:
            user_query: Original user query (any language)
            bot_response: Bot response in English
            target_language: Target language for response (auto-detect if None)
            
        Returns:
            Dictionary with translations and metadata
        """
        logger.info("Starting query-response translation workflow")
        
        # Step 1: Detect user's language from query
        user_language = self.detect_language(user_query)
        
        # Step 2: Translate query to English (for RAG processing)
        english_query, detected_lang = self.translate(
            text=user_query,
            src_lang=user_language,
            dest_lang='en'
        )
        
        # Step 3: Determine response language
        response_language = target_language or user_language
        
        # Step 4: Translate bot response back to user's language
        translated_response, _ = self.translate(
            text=bot_response,
            src_lang='en',
            dest_lang=response_language
        )
        
        result = {
            'original_query': user_query,
            'english_query': english_query,
            'detected_language': detected_lang,
            'language_name': self.SUPPORTED_LANGUAGES.get(detected_lang, 'Unknown'),
            'english_response': bot_response,
            'translated_response': translated_response,
            'response_language': response_language
        }
        
        logger.info(f"Translation workflow complete: {detected_lang} → en → {response_language}")
        return result
    
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Return dictionary of supported languages"""
        return self.SUPPORTED_LANGUAGES.copy()
    
    
    def is_language_supported(self, lang_code: str) -> bool:
        """Check if a language is supported"""
        return lang_code in self.SUPPORTED_LANGUAGES
    
    
    def clear_cache(self):
        """Clear translation cache"""
        self.translation_cache.clear()
        logger.info("Translation cache cleared")


# Utility function for testing
def test_translation_service():
    """Test the translation service"""
    
    service = TranslationService()
    
    print("\n" + "="*60)
    print("TESTING TRANSLATION SERVICE")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            'query': 'मुझे छात्रवृत्ति के बारे में बताओ',
            'response': 'Scholarships are available for merit and need-based students. Apply before March 31st.',
            'description': 'Hindi query'
        },
        {
            'query': 'ફી ભરવાની છેલ્લી તારીખ ક્યારે છે?',
            'response': 'The fee payment deadline is January 31st, 2025.',
            'description': 'Gujarati query'
        },
        {
            'query': 'What are the hostel facilities?',
            'response': 'Hostel facilities include 24/7 security, WiFi, mess, and common room.',
            'description': 'English query'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test['description']} ---")
        print(f"User Query: {test['query']}")
        
        result = service.translate_query_response(
            user_query=test['query'],
            bot_response=test['response']
        )
        
        print(f"Detected Language: {result['language_name']} ({result['detected_language']})")
        print(f"English Query: {result['english_query']}")
        print(f"English Response: {result['english_response']}")
        print(f"Translated Response: {result['translated_response']}")
    
    # Test language support
    print(f"\n\nSupported Languages ({len(service.SUPPORTED_LANGUAGES)}):")
    for code, name in service.SUPPORTED_LANGUAGES.items():
        print(f"  - {name} ({code})")


if __name__ == "__main__":
    test_translation_service()