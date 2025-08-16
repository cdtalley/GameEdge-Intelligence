from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from ..core.database import Base


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CHURNED = "churned"


class UserTier(str, enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Demographics
    first_name = Column(String(50))
    last_name = Column(String(50))
    date_of_birth = Column(DateTime)
    gender = Column(String(10))
    country = Column(String(50))
    state = Column(String(50))
    city = Column(String(50))
    zip_code = Column(String(20))
    
    # Betting Profile
    favorite_sport = Column(String(50))
    favorite_team = Column(String(100))
    betting_experience = Column(String(20))  # beginner, intermediate, expert
    risk_tolerance = Column(String(20))  # low, medium, high
    
    # Financial Metrics
    total_deposits = Column(Float, default=0.0)
    total_withdrawals = Column(Float, default=0.0)
    current_balance = Column(Float, default=0.0)
    lifetime_value = Column(Float, default=0.0)
    average_bet_size = Column(Float, default=0.0)
    
    # Behavioral Metrics
    total_bets = Column(Integer, default=0)
    winning_bets = Column(Integer, default=0)
    losing_bets = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    
    # RFM Analysis Fields
    recency_score = Column(Integer, default=0)  # Days since last activity
    frequency_score = Column(Integer, default=0)  # Activity frequency
    monetary_score = Column(Integer, default=0)  # Monetary value
    
    # Segmentation
    user_tier = Column(Enum(UserTier), default=UserTier.BRONZE)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    segment_id = Column(Integer, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    last_activity = Column(DateTime(timezone=True))
    
    # Churn Prediction
    churn_probability = Column(Float, default=0.0)
    churn_risk_level = Column(String(20))  # low, medium, high
    
    # Relationships
    bets = relationship("Bet", back_populates="user")
    interactions = relationship("Interaction", back_populates="user")
    user_segments = relationship("UserSegment", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', tier='{self.user_tier}')>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username
    
    @property
    def is_active(self):
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_high_value(self):
        return self.user_tier in [UserTier.GOLD, UserTier.PLATINUM, UserTier.DIAMOND]
    
    def calculate_rfm_scores(self):
        """Calculate RFM scores based on user behavior"""
        # This would be implemented with actual business logic
        pass
