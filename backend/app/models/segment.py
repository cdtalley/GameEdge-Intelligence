from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, Enum, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from ..core.database import Base


class SegmentType(str, enum.Enum):
    RFM = "rfm"
    CLUSTERING = "clustering"
    BEHAVIORAL = "behavioral"
    DEMOGRAPHIC = "demographic"
    HYBRID = "hybrid"


class SegmentPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Segment(Base):
    __tablename__ = "segments"

    id = Column(Integer, primary_key=True, index=True)
    
    # Segment Information
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    segment_type = Column(Enum(SegmentType), nullable=False)
    priority = Column(Enum(SegmentPriority), default=SegmentPriority.MEDIUM)
    
    # Segmentation Criteria
    criteria = Column(JSON, nullable=False)  # Store segmentation rules
    # Example: {"rfm_recency": ">30", "rfm_frequency": ">10", "rfm_monetary": ">1000"}
    
    # ML Model Information
    model_used = Column(String(100))  # Which algorithm created this segment
    model_version = Column(String(50))
    confidence_threshold = Column(Float, default=0.8)
    
    # Segment Statistics
    user_count = Column(Integer, default=0)
    total_value = Column(Float, default=0.0)
    average_value = Column(Float, default=0.0)
    
    # RFM Scores (if applicable)
    avg_recency_score = Column(Float)
    avg_frequency_score = Column(Float)
    avg_monetary_score = Column(Float)
    
    # Behavioral Metrics
    avg_bet_size = Column(Float)
    avg_win_rate = Column(Float)
    churn_risk = Column(Float)
    lifetime_value = Column(Float)
    
    # Business Rules
    is_active = Column(Boolean, default=True)
    auto_update = Column(Boolean, default=True)  # Whether to automatically update segment membership
    update_frequency = Column(String(20))  # daily, weekly, monthly
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_updated = Column(DateTime(timezone=True))  # When segment was last recalculated
    
    # Relationships
    user_segments = relationship("UserSegment", back_populates="segment")
    
    def __repr__(self):
        return f"<Segment(id={self.id}, name='{self.name}', type='{self.segment_type}', users={self.user_count})>"
    
    @property
    def is_rfm_based(self):
        return self.segment_type == SegmentType.RFM
    
    @property
    def is_clustering_based(self):
        return self.segment_type == SegmentType.CLUSTERING
    
    def get_criteria_value(self, key: str):
        """Get value for a specific segmentation criterion"""
        if self.criteria and key in self.criteria:
            return self.criteria[key]
        return None
    
    def add_criteria(self, key: str, value):
        """Add or update segmentation criterion"""
        if not self.criteria:
            self.criteria = {}
        self.criteria[key] = value
    
    def calculate_rfm_averages(self, users):
        """Calculate average RFM scores for users in this segment"""
        if not users:
            return
        
        recency_scores = [u.recency_score for u in users if u.recency_score is not None]
        frequency_scores = [u.frequency_score for u in users if u.frequency_score is not None]
        monetary_scores = [u.monetary_score for u in users if u.monetary_score is not None]
        
        if recency_scores:
            self.avg_recency_score = sum(recency_scores) / len(recency_scores)
        if frequency_scores:
            self.avg_frequency_score = sum(frequency_scores) / len(frequency_scores)
        if monetary_scores:
            self.avg_monetary_score = sum(monetary_scores) / len(monetary_scores)


class UserSegment(Base):
    __tablename__ = "user_segments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    segment_id = Column(Integer, ForeignKey("segments.id"), nullable=False, index=True)
    
    # Assignment Details
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    confidence_score = Column(Float)  # How confident the model is about this assignment
    assignment_method = Column(String(50))  # automatic, manual, hybrid
    
    # Segment Performance
    segment_value = Column(Float, default=0.0)  # User's value within this segment
    segment_rank = Column(Integer)  # User's rank within the segment
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_segments")
    segment = relationship("Segment", back_populates="user_segments")
    
    def __repr__(self):
        return f"<UserSegment(user_id={self.user_id}, segment_id={self.segment_id}, confidence={self.confidence_score})>"
    
    @property
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if the segment assignment is high confidence"""
        return self.confidence_score and self.confidence_score >= threshold
