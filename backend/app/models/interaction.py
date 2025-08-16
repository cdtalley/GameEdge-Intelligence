from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, Enum, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from ..core.database import Base


class InteractionType(str, enum.Enum):
    REVIEW = "review"
    FEEDBACK = "feedback"
    SUPPORT_TICKET = "support_ticket"
    SOCIAL_MEDIA = "social_media"
    APP_REVIEW = "app_review"
    BET_COMMENT = "bet_comment"
    GENERAL = "general"


class SentimentLabel(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Interaction Details
    interaction_type = Column(Enum(InteractionType), nullable=False)
    title = Column(String(200))
    content = Column(Text, nullable=False)
    source = Column(String(100))  # web, mobile, api, external
    
    # Sentiment Analysis Results
    sentiment_label = Column(Enum(SentimentLabel))
    sentiment_score = Column(Float)  # -1.0 to 1.0
    confidence_score = Column(Float)  # 0.0 to 1.0
    
    # Aspect-based Sentiment
    aspects = Column(JSON)  # Store aspect-specific sentiment scores
    # Example: {"customer_service": 0.8, "odds": -0.3, "platform": 0.6}
    
    # ML Model Information
    model_used = Column(String(100))  # Which model made the prediction
    model_version = Column(String(50))
    preprocessing_steps = Column(JSON)  # Store preprocessing pipeline info
    
    # Context Information
    related_bet_id = Column(Integer, ForeignKey("bets.id"))
    sport = Column(String(50))
    team = Column(String(100))
    event = Column(String(200))
    
    # User Experience Metrics
    rating = Column(Integer)  # 1-5 star rating if applicable
    category = Column(String(100))  # General category of the interaction
    
    # Metadata
    language = Column(String(10), default="en")
    is_public = Column(Boolean, default=True)
    is_moderated = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True))  # When sentiment analysis was completed
    
    # External References
    external_id = Column(String(100))  # For integration with external systems
    url = Column(String(500))  # If the interaction came from a URL
    
    # Relationships
    user = relationship("User", back_populates="interactions")
    related_bet = relationship("Bet")
    
    def __repr__(self):
        return f"<Interaction(id={self.id}, user_id={self.user_id}, type='{self.interaction_type}', sentiment='{self.sentiment_label}')>"
    
    @property
    def is_positive(self):
        return self.sentiment_label == SentimentLabel.POSITIVE
    
    @property
    def is_negative(self):
        return self.sentiment_label == SentimentLabel.NEGATIVE
    
    @property
    def is_neutral(self):
        return self.sentiment_label == SentimentLabel.NEUTRAL
    
    @property
    def sentiment_magnitude(self):
        """Return the absolute value of sentiment score"""
        return abs(self.sentiment_score) if self.sentiment_score else 0.0
    
    def get_aspect_sentiment(self, aspect_name: str) -> float:
        """Get sentiment score for a specific aspect"""
        if self.aspects and aspect_name in self.aspects:
            return self.aspects[aspect_name]
        return 0.0
    
    def add_aspect_sentiment(self, aspect_name: str, score: float):
        """Add or update aspect-specific sentiment score"""
        if not self.aspects:
            self.aspects = {}
        self.aspects[aspect_name] = score
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if the sentiment prediction is high confidence"""
        return self.confidence_score and self.confidence_score >= threshold
