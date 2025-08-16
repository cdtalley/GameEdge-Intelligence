import logging
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import torch
import json
import os
from datetime import datetime

from ..core.config import settings

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Multi-model sentiment analysis engine with BERT-based transformers and traditional ML fallback.
    Supports sports betting specific language and aspect-based sentiment analysis.
    """
    
    def __init__(self):
        self.transformer_pipeline = None
        self.fallback_pipeline = None
        self.aspect_extractor = None
        self.is_initialized = False
        self.model_info = {}
        
        # Sports betting specific terms and aspects
        self.sports_aspects = [
            "odds", "betting", "platform", "customer_service", "payouts",
            "user_interface", "mobile_app", "website", "promotions", "bonuses",
            "game_selection", "live_betting", "cash_out", "deposits", "withdrawals"
        ]
        
        # Sports betting slang and terminology
        self.sports_terms = [
            "parlay", "teaser", "futures", "props", "spread", "moneyline", "over/under",
            "vig", "juice", "chalk", "dog", "push", "cover", "ATS", "ML", "OU"
        ]
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize both transformer and fallback models"""
        try:
            # Initialize transformer model
            self._setup_transformer_model()
            
            # Initialize fallback ML model
            self._setup_fallback_model()
            
            # Initialize aspect extraction
            self._setup_aspect_extraction()
            
            self.is_initialized = True
            logger.info("Sentiment analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize sentiment analyzer: {e}")
            self.is_initialized = False
    
    def _setup_transformer_model(self):
        """Setup the BERT-based transformer model"""
        try:
            model_name = settings.SENTIMENT_MODEL_NAME
            
            # Use cardiffnlp/twitter-roberta-base-sentiment-latest for sports betting context
            if "cardiffnlp" in model_name:
                # This model is trained on Twitter data and handles informal language well
                self.transformer_pipeline = pipeline(
                    "sentiment-analysis",
                    model=model_name,
                    tokenizer=model_name,
                    device=0 if torch.cuda.is_available() else -1
                )
            else:
                # Fallback to general sentiment model
                self.transformer_pipeline = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=0 if torch.cuda.is_available() else -1
                )
            
            self.model_info["transformer"] = {
                "name": model_name,
                "type": "transformer",
                "device": "cuda" if torch.cuda.is_available() else "cpu"
            }
            
            logger.info(f"Transformer model loaded: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load transformer model: {e}")
            self.transformer_pipeline = None
    
    def _setup_fallback_model(self):
        """Setup traditional ML fallback model"""
        try:
            # Simple TF-IDF + Logistic Regression pipeline
            self.fallback_pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=10000,
                    ngram_range=(1, 2),
                    stop_words='english'
                )),
                ('classifier', LogisticRegression(random_state=42))
            ])
            
            # Train on basic sentiment data (this would be replaced with actual training data)
            self._train_fallback_model()
            
            self.model_info["fallback"] = {
                "name": "TF-IDF + Logistic Regression",
                "type": "traditional_ml",
                "features": "TF-IDF with bigrams"
            }
            
            logger.info("Fallback ML model initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup fallback model: {e}")
            self.fallback_pipeline = None
    
    def _setup_aspect_extraction(self):
        """Setup aspect-based sentiment extraction"""
        try:
            # Simple keyword-based aspect extraction
            # In production, this would use more sophisticated NLP techniques
            self.aspect_extractor = {
                "odds": ["odds", "line", "spread", "moneyline", "juice", "vig"],
                "betting": ["bet", "wager", "stake", "parlay", "teaser"],
                "platform": ["app", "website", "interface", "mobile", "desktop"],
                "customer_service": ["support", "help", "service", "agent", "representative"],
                "payouts": ["payout", "withdrawal", "cash", "money", "funds"],
                "promotions": ["bonus", "promo", "offer", "deal", "free"],
                "game_selection": ["sports", "games", "teams", "leagues", "events"]
            }
            
            logger.info("Aspect extraction initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup aspect extraction: {e}")
            self.aspect_extractor = None
    
    def _train_fallback_model(self):
        """Train the fallback ML model with sample data"""
        try:
            # This is a simplified training with dummy data
            # In production, this would use the Sentiment140 dataset or similar
            sample_texts = [
                "Great odds on the game today!",
                "Terrible customer service experience",
                "Love the new mobile app interface",
                "Withdrawal process is too slow",
                "Amazing bonus offers this week",
                "Platform is easy to use",
                "Odds are not competitive",
                "Fast payouts, very satisfied",
                "Difficult to navigate the website",
                "Excellent live betting features"
            ]
            
            sample_labels = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1]  # 1=positive, 0=negative
            
            # Fit the pipeline
            self.fallback_pipeline.fit(sample_texts, sample_labels)
            
            logger.info("Fallback model trained with sample data")
            
        except Exception as e:
            logger.error(f"Failed to train fallback model: {e}")
    
    def analyze_sentiment(self, text: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze sentiment of given text using multi-model approach.
        
        Args:
            text: Text to analyze
            user_id: Optional user ID for context
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not self.is_initialized:
            return self._get_error_response("Sentiment analyzer not initialized")
        
        try:
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Try transformer model first
            transformer_result = self._analyze_with_transformer(processed_text)
            
            # If transformer fails, use fallback
            if transformer_result.get("error"):
                logger.warning("Transformer model failed, using fallback")
                fallback_result = self._analyze_with_fallback(processed_text)
                result = fallback_result
                result["model_used"] = "fallback"
            else:
                result = transformer_result
                result["model_used"] = "transformer"
            
            # Extract aspects
            aspects = self._extract_aspects(processed_text)
            result["aspects"] = aspects
            
            # Add metadata
            result.update({
                "user_id": user_id,
                "text": text,
                "processed_text": processed_text,
                "timestamp": datetime.utcnow().isoformat(),
                "model_info": self.model_info.get(result["model_used"], {})
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return self._get_error_response(str(e))
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Basic cleaning (in production, use more sophisticated NLP preprocessing)
        return text
    
    def _analyze_with_transformer(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using transformer model"""
        try:
            if not self.transformer_pipeline:
                return {"error": "Transformer pipeline not available"}
            
            # Get prediction
            result = self.transformer_pipeline(text)[0]
            
            # Map labels to our format
            label_mapping = {
                "LABEL_0": "negative",
                "LABEL_1": "neutral", 
                "LABEL_2": "positive"
            }
            
            sentiment_label = label_mapping.get(result["label"], "neutral")
            confidence_score = result["score"]
            
            # Convert to -1 to 1 scale
            if sentiment_label == "positive":
                sentiment_score = confidence_score
            elif sentiment_label == "negative":
                sentiment_score = -confidence_score
            else:
                sentiment_score = 0.0
            
            return {
                "sentiment_label": sentiment_label,
                "sentiment_score": sentiment_score,
                "confidence_score": confidence_score,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Transformer analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_with_fallback(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using fallback ML model"""
        try:
            if not self.fallback_pipeline:
                return {"error": "Fallback pipeline not available"}
            
            # Get prediction
            prediction = self.fallback_pipeline.predict([text])[0]
            confidence = self.fallback_pipeline.predict_proba([text])[0].max()
            
            # Map prediction to sentiment
            sentiment_label = "positive" if prediction == 1 else "negative"
            sentiment_score = confidence if prediction == 1 else -confidence
            
            return {
                "sentiment_label": sentiment_label,
                "sentiment_score": sentiment_score,
                "confidence_score": confidence,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Fallback analysis failed: {e}")
            return {"error": str(e)}
    
    def _extract_aspects(self, text: str) -> Dict[str, float]:
        """Extract aspect-based sentiment scores"""
        aspects = {}
        
        if not self.aspect_extractor:
            return aspects
        
        try:
            for aspect, keywords in self.aspect_extractor.items():
                # Simple keyword-based aspect detection
                # In production, use more sophisticated NLP techniques
                keyword_count = sum(1 for keyword in keywords if keyword in text)
                
                if keyword_count > 0:
                    # Simple scoring based on keyword presence
                    # This is a placeholder - real implementation would use aspect-specific sentiment
                    aspects[aspect] = 0.1 * keyword_count  # Basic scoring
                else:
                    aspects[aspect] = 0.0
            
            return aspects
            
        except Exception as e:
            logger.error(f"Aspect extraction failed: {e}")
            return {}
    
    def _get_error_response(self, error_message: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "sentiment_label": "neutral",
            "sentiment_score": 0.0,
            "confidence_score": 0.0,
            "error": error_message,
            "aspects": {},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models"""
        return {
            "is_initialized": self.is_initialized,
            "transformer_available": self.transformer_pipeline is not None,
            "fallback_available": self.fallback_pipeline is not None,
            "aspect_extraction_available": self.aspect_extractor is not None,
            "model_info": self.model_info,
            "sports_aspects": self.sports_aspects,
            "sports_terms": self.sports_terms
        }
    
    def reload_models(self):
        """Reload all models"""
        logger.info("Reloading sentiment analysis models")
        self._initialize_models()
        return self.get_model_status()


# Global instance
sentiment_analyzer = SentimentAnalyzer()
