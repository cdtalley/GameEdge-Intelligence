from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from ..core.database import Base


class BetStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    WON = "won"
    LOST = "lost"
    CANCELLED = "cancelled"
    VOID = "void"


class BetType(str, enum.Enum):
    SINGLE = "single"
    PARLAY = "parlay"
    TEASER = "teaser"
    FUTURES = "futures"
    PROPS = "props"


class Sport(str, enum.Enum):
    FOOTBALL = "football"
    BASKETBALL = "basketball"
    BASEBALL = "baseball"
    HOCKEY = "hockey"
    SOCCER = "soccer"
    TENNIS = "tennis"
    GOLF = "golf"
    MMA = "mma"
    BOXING = "boxing"
    OTHER = "other"


class Bet(Base):
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Bet Details
    bet_type = Column(Enum(BetType), nullable=False)
    sport = Column(Enum(Sport), nullable=False)
    league = Column(String(100))
    home_team = Column(String(100))
    away_team = Column(String(100))
    bet_selection = Column(String(200))  # What they're betting on
    odds = Column(Float, nullable=False)
    stake = Column(Float, nullable=False)
    potential_payout = Column(Float, nullable=False)
    
    # Game Information
    game_date = Column(DateTime)
    game_id = Column(String(100))
    season = Column(String(20))
    
    # Betting Line Information
    opening_odds = Column(Float)
    closing_odds = Column(Float)
    line_movement = Column(Float)  # Change in odds
    
    # Outcome
    status = Column(Enum(BetStatus), default=BetStatus.PENDING)
    result = Column(String(50))  # win, loss, push
    actual_payout = Column(Float, default=0.0)
    profit_loss = Column(Float, default=0.0)
    
    # Risk Assessment
    risk_level = Column(String(20))  # low, medium, high
    confidence_score = Column(Float)  # User's confidence in the bet
    
    # Timestamps
    placed_at = Column(DateTime(timezone=True), server_default=func.now())
    settled_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    
    # Additional Metadata
    notes = Column(Text)
    external_bet_id = Column(String(100))  # For integration with external systems
    
    # Relationships
    user = relationship("User", back_populates="bets")
    
    def __repr__(self):
        return f"<Bet(id={self.id}, user_id={self.user_id}, sport='{self.sport}', status='{self.status}')>"
    
    @property
    def is_winner(self):
        return self.status == BetStatus.WON
    
    @property
    def is_loser(self):
        return self.status == BetStatus.LOST
    
    @property
    def is_pending(self):
        return self.status in [BetStatus.PENDING, BetStatus.ACTIVE]
    
    @property
    def roi(self):
        """Return on Investment"""
        if self.stake > 0:
            return (self.profit_loss / self.stake) * 100
        return 0.0
    
    def calculate_potential_payout(self):
        """Calculate potential payout based on odds and stake"""
        if self.odds > 0:
            if self.odds >= 2.0:  # American odds
                self.potential_payout = self.stake * (self.odds - 1)
            else:  # Decimal odds
                self.potential_payout = self.stake * self.odds
        return self.potential_payout
