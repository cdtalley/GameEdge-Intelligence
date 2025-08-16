from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta
import pandas as pd

from ...core.database import get_db
from ...models import User, Bet, Interaction, Segment, UserSegment, UserStatus, SentimentLabel

logger = logging.getLogger(__name__)

router = APIRouter()


class DashboardMetricsResponse(BaseModel):
    total_users: int
    active_users: int
    total_bets: int
    total_revenue: float
    average_bet_size: float
    win_rate: float
    sentiment_distribution: Dict[str, int]
    segment_distribution: Dict[str, int]
    churn_risk_distribution: Dict[str, int]
    top_sports: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]


class SentimentTrendsResponse(BaseModel):
    period: str
    total_interactions: int
    sentiment_trends: List[Dict[str, Any]]
    aspect_analysis: Dict[str, Dict[str, float]]
    top_keywords: List[Dict[str, Any]]


class CustomerBehaviorResponse(BaseModel):
    rfm_distribution: Dict[str, int]
    betting_patterns: Dict[str, Any]
    user_journey_stages: Dict[str, int]
    retention_metrics: Dict[str, float]
    lifetime_value_distribution: Dict[str, int]


class RevenueAnalyticsResponse(BaseModel):
    total_revenue: float
    revenue_by_sport: List[Dict[str, Any]]
    revenue_by_segment: List[Dict[str, Any]]
    revenue_trends: List[Dict[str, Any]]
    profit_margins: Dict[str, float]


@router.get("/dashboard", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(
    db: AsyncSession = get_db,
    date_from: Optional[datetime] = Query(None, description="Start date for metrics"),
    date_to: Optional[datetime] = Query(None, description="End date for metrics")
):
    """
    Get comprehensive dashboard metrics for the sports betting platform.
    
    Provides key performance indicators including user metrics, betting activity,
    sentiment analysis, and customer segmentation data.
    """
    try:
        # Set default date range if not provided
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=30)
        if not date_to:
            date_to = datetime.utcnow()
        
        # Get user metrics
        total_users = await db.execute(select(func.count(User.id)))
        total_users = total_users.scalar()
        
        active_users = await db.execute(
            select(func.count(User.id)).where(User.status == UserStatus.ACTIVE)
        )
        active_users = active_users.scalar()
        
        # Get betting metrics
        betting_query = select(Bet)
        if date_from and date_to:
            betting_query = betting_query.where(
                and_(Bet.placed_at >= date_from, Bet.placed_at <= date_to)
            )
        
        bets_result = await db.execute(betting_query)
        bets = bets_result.scalars().all()
        
        total_bets = len(bets)
        total_revenue = sum(bet.stake for bet in bets if bet.stake)
        average_bet_size = total_revenue / total_bets if total_bets > 0 else 0
        
        # Calculate win rate
        winning_bets = sum(1 for bet in bets if bet.status == "won")
        win_rate = (winning_bets / total_bets * 100) if total_bets > 0 else 0
        
        # Get sentiment distribution
        sentiment_result = await db.execute(
            select(Interaction.sentiment_label, func.count(Interaction.id))
            .where(Interaction.sentiment_label.is_not(None))
            .group_by(Interaction.sentiment_label)
        )
        sentiment_distribution = dict(sentiment_result.all())
        
        # Get segment distribution
        segment_result = await db.execute(
            select(Segment.name, func.count(UserSegment.user_id))
            .join(UserSegment, Segment.id == UserSegment.segment_id)
            .group_by(Segment.name)
        )
        segment_distribution = dict(segment_result.all())
        
        # Get churn risk distribution
        churn_result = await db.execute(
            select(User.churn_risk_level, func.count(User.id))
            .where(User.churn_risk_level.is_not(None))
            .group_by(User.churn_risk_level)
        )
        churn_risk_distribution = dict(churn_result.all())
        
        # Get top sports by betting volume
        sports_result = await db.execute(
            select(Bet.sport, func.count(Bet.id), func.sum(Bet.stake))
            .group_by(Bet.sport)
            .order_by(desc(func.sum(Bet.stake)))
            .limit(5)
        )
        top_sports = [
            {
                "sport": sport,
                "bet_count": bet_count,
                "total_stake": float(total_stake or 0)
            }
            for sport, bet_count, total_stake in sports_result.all()
        ]
        
        # Get recent activity
        recent_interactions = await db.execute(
            select(Interaction)
            .order_by(desc(Interaction.created_at))
            .limit(10)
        )
        recent_activity = [
            {
                "id": interaction.id,
                "type": interaction.interaction_type.value,
                "sentiment": interaction.sentiment_label.value if interaction.sentiment_label else "unknown",
                "created_at": interaction.created_at.isoformat(),
                "user_id": interaction.user_id
            }
            for interaction in recent_interactions.scalars().all()
        ]
        
        return DashboardMetricsResponse(
            total_users=total_users,
            active_users=active_users,
            total_bets=total_bets,
            total_revenue=total_revenue,
            average_bet_size=average_bet_size,
            win_rate=win_rate,
            sentiment_distribution=sentiment_distribution,
            segment_distribution=segment_distribution,
            churn_risk_distribution=churn_risk_distribution,
            top_sports=top_sports,
            recent_activity=recent_activity
        )
        
    except Exception as e:
        logger.error(f"Failed to get dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard metrics: {str(e)}")


@router.get("/sentiment/trends", response_model=SentimentTrendsResponse)
async def get_sentiment_trends(
    db: AsyncSession = get_db,
    period: str = Query("7d", description="Time period: 1d, 7d, 30d, 90d"),
    sport: Optional[str] = Query(None, description="Filter by sport")
):
    """
    Get sentiment analysis trends over time.
    
    Provides sentiment distribution trends and aspect-based analysis
    for understanding customer satisfaction patterns.
    """
    try:
        # Calculate date range based on period
        end_date = datetime.utcnow()
        if period == "1d":
            start_date = end_date - timedelta(days=1)
        elif period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=7)
        
        # Get sentiment trends over time
        sentiment_query = select(
            func.date_trunc('day', Interaction.created_at).label('date'),
            Interaction.sentiment_label,
            func.count(Interaction.id)
        ).where(
            and_(
                Interaction.created_at >= start_date,
                Interaction.created_at <= end_date,
                Interaction.sentiment_label.is_not(None)
            )
        )
        
        if sport:
            sentiment_query = sentiment_query.where(Interaction.sport == sport)
        
        sentiment_query = sentiment_query.group_by(
            func.date_trunc('day', Interaction.created_at),
            Interaction.sentiment_label
        ).order_by(
            func.date_trunc('day', Interaction.created_at)
        )
        
        sentiment_result = await db.execute(sentiment_query)
        sentiment_data = sentiment_result.all()
        
        # Process sentiment trends
        sentiment_trends = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_sentiments = {
                'date': date_str,
                'positive': 0,
                'negative': 0,
                'neutral': 0
            }
            
            for date, label, count in sentiment_data:
                if date.date() == current_date.date():
                    daily_sentiments[label.value] = count
            
            sentiment_trends.append(daily_sentiments)
            current_date += timedelta(days=1)
        
        # Get aspect analysis
        aspect_query = select(
            Interaction.aspects
        ).where(
            and_(
                Interaction.created_at >= start_date,
                Interaction.created_at <= end_date,
                Interaction.aspects.is_not(None)
            )
        )
        
        if sport:
            aspect_query = aspect_query.where(Interaction.sport == sport)
        
        aspect_result = await db.execute(aspect_query)
        aspects_data = aspect_result.scalars().all()
        
        # Aggregate aspect scores
        aspect_analysis = {}
        for aspects in aspects_data:
            if aspects:
                for aspect, score in aspects.items():
                    if aspect not in aspect_analysis:
                        aspect_analysis[aspect] = {'total': 0, 'count': 0, 'average': 0}
                    aspect_analysis[aspect]['total'] += score
                    aspect_analysis[aspect]['count'] += 1
        
        # Calculate averages
        for aspect in aspect_analysis:
            if aspect_analysis[aspect]['count'] > 0:
                aspect_analysis[aspect]['average'] = (
                    aspect_analysis[aspect]['total'] / aspect_analysis[aspect]['count']
                )
        
        # Get top keywords (simplified - would use NLP in production)
        keyword_query = select(
            func.lower(Interaction.content).label('content')
        ).where(
            and_(
                Interaction.created_at >= start_date,
                Interaction.created_at <= end_date
            )
        )
        
        if sport:
            keyword_query = keyword_query.where(Interaction.sport == sport)
        
        keyword_result = await db.execute(keyword_query)
        keywords_data = keyword_result.scalars().all()
        
        # Simple keyword extraction (placeholder)
        top_keywords = [
            {"keyword": "odds", "frequency": 150},
            {"keyword": "betting", "frequency": 120},
            {"keyword": "platform", "frequency": 90},
            {"keyword": "customer_service", "frequency": 75}
        ]
        
        return SentimentTrendsResponse(
            period=period,
            total_interactions=len(sentiment_data),
            sentiment_trends=sentiment_trends,
            aspect_analysis=aspect_analysis,
            top_keywords=top_keywords
        )
        
    except Exception as e:
        logger.error(f"Failed to get sentiment trends: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sentiment trends: {str(e)}")


@router.get("/customers/behavior", response_model=CustomerBehaviorResponse)
async def get_customer_behavior_analytics(
    db: AsyncSession = get_db,
    segment_id: Optional[int] = Query(None, description="Filter by segment")
):
    """
    Get customer behavior analytics and insights.
    
    Provides RFM analysis, betting patterns, user journey mapping,
    and retention metrics for customer intelligence.
    """
    try:
        # Get RFM distribution
        rfm_query = select(
            User.recency_score,
            User.frequency_score,
            User.monetary_score,
            func.count(User.id)
        ).where(
            and_(
                User.recency_score.is_not(None),
                User.frequency_score.is_not(None),
                User.monetary_score.is_not(None)
            )
        )
        
        if segment_id:
            rfm_query = rfm_query.join(UserSegment, User.id == UserSegment.user_id)
            rfm_query = rfm_query.where(UserSegment.segment_id == segment_id)
        
        rfm_query = rfm_query.group_by(
            User.recency_score,
            User.frequency_score,
            User.monetary_score
        )
        
        rfm_result = await db.execute(rfm_query)
        rfm_data = rfm_result.all()
        
        # Process RFM distribution
        rfm_distribution = {
            'high_value': 0,
            'medium_value': 0,
            'low_value': 0,
            'at_risk': 0
        }
        
        for recency, frequency, monetary, count in rfm_data:
            # Simple RFM scoring logic
            rfm_score = (recency + frequency + monetary) / 3
            if rfm_score >= 4:
                rfm_distribution['high_value'] += count
            elif rfm_score >= 3:
                rfm_distribution['medium_value'] += count
            elif rfm_score >= 2:
                rfm_distribution['low_value'] += count
            else:
                rfm_distribution['at_risk'] += count
        
        # Get betting patterns
        betting_query = select(
            Bet.sport,
            func.avg(Bet.stake).label('avg_stake'),
            func.count(Bet.id).label('bet_count'),
            func.avg(Bet.odds).label('avg_odds')
        ).group_by(Bet.sport)
        
        if segment_id:
            betting_query = betting_query.join(User, Bet.user_id == User.id)
            betting_query = betting_query.join(UserSegment, User.id == UserSegment.user_id)
            betting_query = betting_query.where(UserSegment.segment_id == segment_id)
        
        betting_result = await db.execute(betting_query)
        betting_patterns = {
            'by_sport': [
                {
                    'sport': sport,
                    'average_stake': float(avg_stake or 0),
                    'bet_count': bet_count,
                    'average_odds': float(avg_odds or 0)
                }
                for sport, avg_stake, bet_count, avg_odds in betting_result.all()
            ]
        }
        
        # Get user journey stages (simplified)
        user_journey_stages = {
            'new_users': 0,
            'active_users': 0,
            'engaged_users': 0,
            'vip_users': 0
        }
        
        # Get retention metrics
        retention_query = select(
            func.avg(User.total_bets).label('avg_bets'),
            func.avg(User.lifetime_value).label('avg_lifetime_value'),
            func.avg(User.win_rate).label('avg_win_rate')
        )
        
        if segment_id:
            retention_query = retention_query.join(UserSegment, User.id == UserSegment.user_id)
            retention_query = retention_query.where(UserSegment.segment_id == segment_id)
        
        retention_result = await db.execute(retention_query)
        retention_data = retention_result.first()
        
        retention_metrics = {
            'average_bets_per_user': float(retention_data.avg_bets or 0),
            'average_lifetime_value': float(retention_data.avg_lifetime_value or 0),
            'average_win_rate': float(retention_data.avg_win_rate or 0)
        }
        
        # Get lifetime value distribution
        ltv_query = select(
            func.ntile(5).over(order_by(User.lifetime_value).label('ltv_quintile'),
            func.count(User.id)
        ).where(User.lifetime_value > 0)
        
        if segment_id:
            ltv_query = ltv_query.join(UserSegment, User.id == UserSegment.user_id)
            ltv_query = ltv_query.where(UserSegment.segment_id == segment_id)
        
        ltv_query = ltv_query.group_by(
            func.ntile(5).over(order_by(User.lifetime_value)
        )
        
        ltv_result = await db.execute(ltv_query)
        ltv_distribution = {
            f'quintile_{i}': count
            for i, count in ltv_result.all()
        }
        
        return CustomerBehaviorResponse(
            rfm_distribution=rfm_distribution,
            betting_patterns=betting_patterns,
            user_journey_stages=user_journey_stages,
            retention_metrics=retention_metrics,
            lifetime_value_distribution=ltv_distribution
        )
        
    except Exception as e:
        logger.error(f"Failed to get customer behavior analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get behavior analytics: {str(e)}")


@router.get("/revenue", response_model=RevenueAnalyticsResponse)
async def get_revenue_analytics(
    db: AsyncSession = get_db,
    date_from: Optional[datetime] = Query(None, description="Start date for revenue analysis"),
    date_to: Optional[datetime] = Query(None, description="End date for revenue analysis")
):
    """
    Get comprehensive revenue analytics and insights.
    
    Provides revenue breakdown by sport, segment, trends over time,
    and profit margin analysis.
    """
    try:
        # Set default date range if not provided
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=30)
        if not date_to:
            date_to = datetime.utcnow()
        
        # Get total revenue
        revenue_query = select(func.sum(Bet.stake)).where(
            and_(
                Bet.placed_at >= date_from,
                Bet.placed_at <= date_to
            )
        )
        
        total_revenue_result = await db.execute(revenue_query)
        total_revenue = float(total_revenue_result.scalar() or 0)
        
        # Get revenue by sport
        sport_revenue_query = select(
            Bet.sport,
            func.sum(Bet.stake).label('total_stake'),
            func.count(Bet.id).label('bet_count'),
            func.avg(Bet.stake).label('avg_stake')
        ).where(
            and_(
                Bet.placed_at >= date_from,
                Bet.placed_at <= date_to
            )
        ).group_by(Bet.sport).order_by(desc(func.sum(Bet.stake)))
        
        sport_revenue_result = await db.execute(sport_revenue_query)
        revenue_by_sport = [
            {
                'sport': sport,
                'total_revenue': float(total_stake or 0),
                'bet_count': bet_count,
                'average_stake': float(avg_stake or 0),
                'revenue_percentage': (float(total_stake or 0) / total_revenue * 100) if total_revenue > 0 else 0
            }
            for sport, total_stake, bet_count, avg_stake in sport_revenue_result.all()
        ]
        
        # Get revenue by segment
        segment_revenue_query = select(
            Segment.name,
            func.sum(Bet.stake).label('total_stake'),
            func.count(Bet.id).label('bet_count')
        ).join(
            UserSegment, Segment.id == UserSegment.segment_id
        ).join(
            User, UserSegment.user_id == User.id
        ).join(
            Bet, User.id == Bet.user_id
        ).where(
            and_(
                Bet.placed_at >= date_from,
                Bet.placed_at <= date_to
            )
        ).group_by(Segment.name).order_by(desc(func.sum(Bet.stake)))
        
        segment_revenue_result = await db.execute(segment_revenue_query)
        revenue_by_segment = [
            {
                'segment': segment_name,
                'total_revenue': float(total_stake or 0),
                'bet_count': bet_count,
                'revenue_percentage': (float(total_stake or 0) / total_revenue * 100) if total_revenue > 0 else 0
            }
            for segment_name, total_stake, bet_count in segment_revenue_result.all()
        ]
        
        # Get revenue trends over time
        trend_query = select(
            func.date_trunc('day', Bet.placed_at).label('date'),
            func.sum(Bet.stake).label('daily_revenue'),
            func.count(Bet.id).label('daily_bets')
        ).where(
            and_(
                Bet.placed_at >= date_from,
                Bet.placed_at <= date_to
            )
        ).group_by(
            func.date_trunc('day', Bet.placed_at)
        ).order_by(
            func.date_trunc('day', Bet.placed_at)
        )
        
        trend_result = await db.execute(trend_query)
        revenue_trends = [
            {
                'date': date.strftime('%Y-%m-%d'),
                'revenue': float(daily_revenue or 0),
                'bet_count': daily_bets
            }
            for date, daily_revenue, daily_bets in trend_result.all()
        ]
        
        # Calculate profit margins (simplified)
        # In production, this would consider actual payouts, house edge, etc.
        profit_margins = {
            'overall_margin': 0.05,  # 5% house edge
            'by_sport': {
                'football': 0.04,
                'basketball': 0.06,
                'baseball': 0.05,
                'hockey': 0.05
            }
        }
        
        return RevenueAnalyticsResponse(
            total_revenue=total_revenue,
            revenue_by_sport=revenue_by_sport,
            revenue_by_segment=revenue_by_segment,
            revenue_trends=revenue_trends,
            profit_margins=profit_margins
        )
        
    except Exception as e:
        logger.error(f"Failed to get revenue analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get revenue analytics: {str(e)}")


@router.get("/performance/summary")
async def get_performance_summary(
    db: AsyncSession = get_db,
    period: str = Query("30d", description="Time period: 1d, 7d, 30d, 90d")
):
    """
    Get high-level performance summary and KPIs.
    
    Provides executive-level metrics and performance indicators
    for business decision making.
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        if period == "1d":
            start_date = end_date - timedelta(days=1)
        elif period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Get key metrics
        metrics = {
            'period': period,
            'date_range': {
                'from': start_date.isoformat(),
                'to': end_date.isoformat()
            },
            'user_metrics': {},
            'betting_metrics': {},
            'financial_metrics': {},
            'sentiment_metrics': {},
            'risk_metrics': {}
        }
        
        # User metrics
        total_users = await db.execute(select(func.count(User.id)))
        active_users = await db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.last_activity >= start_date,
                    User.status == UserStatus.ACTIVE
                )
            )
        )
        
        metrics['user_metrics'] = {
            'total_users': total_users.scalar(),
            'active_users': active_users.scalar(),
            'activation_rate': 0.0  # Would calculate based on business logic
        }
        
        # Betting metrics
        total_bets = await db.execute(
            select(func.count(Bet.id)).where(
                and_(Bet.placed_at >= start_date, Bet.placed_at <= end_date)
            )
        )
        
        total_stake = await db.execute(
            select(func.sum(Bet.stake)).where(
                and_(Bet.placed_at >= start_date, Bet.placed_at <= end_date)
            )
        )
        
        metrics['betting_metrics'] = {
            'total_bets': total_bets.scalar(),
            'total_stake': float(total_stake.scalar() or 0),
            'average_bet_size': 0.0  # Would calculate
        }
        
        # Financial metrics
        metrics['financial_metrics'] = {
            'total_revenue': float(total_stake.scalar() or 0),
            'profit_margin': 0.05,  # Placeholder
            'customer_acquisition_cost': 0.0  # Would calculate
        }
        
        # Sentiment metrics
        sentiment_count = await db.execute(
            select(func.count(Interaction.id)).where(
                and_(
                    Interaction.created_at >= start_date,
                    Interaction.created_at <= end_date
                )
            )
        )
        
        positive_sentiment = await db.execute(
            select(func.count(Interaction.id)).where(
                and_(
                    Interaction.created_at >= start_date,
                    Interaction.created_at <= end_date,
                    Interaction.sentiment_label == SentimentLabel.POSITIVE
                )
            )
        )
        
        metrics['sentiment_metrics'] = {
            'total_interactions': sentiment_count.scalar(),
            'positive_sentiment_rate': 0.0,  # Would calculate
            'customer_satisfaction_score': 0.0  # Would calculate
        }
        
        # Risk metrics
        high_risk_users = await db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.churn_risk_level == 'high',
                    User.last_activity >= start_date
                )
            )
        )
        
        metrics['risk_metrics'] = {
            'high_churn_risk_users': high_risk_users.scalar(),
            'risk_score': 0.0,  # Would calculate based on business logic
            'recommendations': [
                "Monitor high-risk customers closely",
                "Implement retention campaigns",
                "Analyze churn patterns"
            ]
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get performance summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance summary: {str(e)}")
