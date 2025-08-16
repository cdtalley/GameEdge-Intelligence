from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
import logging
import pandas as pd
from datetime import datetime, timedelta

from ...core.database import get_db
from ...ml.customer_segmentation import segmentation_engine
from ...models import User, Bet, Interaction, Segment, UserSegment, UserStatus

logger = logging.getLogger(__name__)

router = APIRouter()


class CustomerSegmentRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Segment name")
    description: Optional[str] = Field(None, description="Segment description")
    criteria: Dict[str, Any] = Field(..., description="Segmentation criteria")
    segment_type: str = Field(..., description="Type of segment (rfm, clustering, behavioral)")
    priority: Optional[str] = Field("medium", description="Segment priority")
    auto_update: Optional[bool] = Field(True, description="Whether to auto-update segment")


class CustomerSegmentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    segment_type: str
    priority: str
    user_count: int
    total_value: float
    average_value: float
    avg_recency_score: Optional[float]
    avg_frequency_score: Optional[float]
    avg_monetary_score: Optional[float]
    avg_bet_size: Optional[float]
    avg_win_rate: Optional[float]
    churn_risk: Optional[float]
    lifetime_value: Optional[float]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]


class UserSegmentAssignment(BaseModel):
    user_id: int
    segment_id: int
    confidence_score: float
    assignment_method: str
    segment_value: Optional[float]
    segment_rank: Optional[int]


class SegmentationAnalysisRequest(BaseModel):
    method: str = Field("rfm", description="Segmentation method (rfm, clustering, hybrid)")
    clustering_method: Optional[str] = Field("kmeans", description="Clustering method if applicable")
    include_churn_prediction: bool = Field(True, description="Include churn prediction")
    min_users_per_segment: int = Field(10, description="Minimum users per segment")


class SegmentationAnalysisResponse(BaseModel):
    segments_created: int
    total_users_analyzed: int
    rfm_scores_calculated: bool
    clustering_performed: bool
    churn_prediction_completed: bool
    segments: List[CustomerSegmentResponse]
    analysis_summary: Dict[str, Any]


class UserRecommendationResponse(BaseModel):
    user_id: int
    current_segment: str
    churn_risk: str
    recommendations: List[Dict[str, Any]]
    next_best_actions: List[str]


@router.get("/segments", response_model=List[CustomerSegmentResponse])
async def get_customer_segments(
    db: AsyncSession = get_db,
    active_only: bool = Query(True, description="Return only active segments"),
    segment_type: Optional[str] = Query(None, description="Filter by segment type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of segments to return")
):
    """
    Get list of customer segments.
    
    Returns all customer segments with their key metrics and characteristics.
    """
    try:
        query = select(Segment)
        
        if active_only:
            query = query.where(Segment.is_active == True)
        
        if segment_type:
            query = query.where(Segment.segment_type == segment_type)
        
        query = query.limit(limit)
        
        result = await db.execute(query)
        segments = result.scalars().all()
        
        return [CustomerSegmentResponse.from_orm(segment) for segment in segments]
        
    except Exception as e:
        logger.error(f"Failed to get customer segments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get segments: {str(e)}")


@router.post("/segments", response_model=CustomerSegmentResponse)
async def create_customer_segment(
    request: CustomerSegmentRequest,
    db: AsyncSession = get_db
):
    """
    Create a new customer segment.
    
    Allows manual creation of customer segments with custom criteria.
    """
    try:
        # Check if segment name already exists
        existing = await db.execute(
            select(Segment).where(Segment.name == request.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Segment name already exists")
        
        # Create new segment
        segment = Segment(
            name=request.name,
            description=request.description,
            segment_type=request.segment_type,
            priority=request.priority,
            criteria=request.criteria,
            auto_update=request.auto_update,
            is_active=True
        )
        
        db.add(segment)
        await db.commit()
        await db.refresh(segment)
        
        return CustomerSegmentResponse.from_orm(segment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create customer segment: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create segment: {str(e)}")


@router.get("/segments/{segment_id}", response_model=CustomerSegmentResponse)
async def get_customer_segment(
    segment_id: int,
    db: AsyncSession = get_db
):
    """
    Get specific customer segment by ID.
    
    Returns detailed information about a specific customer segment.
    """
    try:
        result = await db.execute(
            select(Segment).where(Segment.id == segment_id)
        )
        segment = result.scalar_one_or_none()
        
        if not segment:
            raise HTTPException(status_code=404, detail="Segment not found")
        
        return CustomerSegmentResponse.from_orm(segment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get customer segment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get segment: {str(e)}")


@router.post("/analyze", response_model=SegmentationAnalysisResponse)
async def analyze_customer_segmentation(
    request: SegmentationAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = get_db
):
    """
    Perform comprehensive customer segmentation analysis.
    
    This endpoint runs the full segmentation pipeline including:
    - RFM score calculation
    - Customer clustering
    - Churn prediction
    - Segment creation and assignment
    """
    try:
        # Get user data for analysis
        users_data = await get_users_data_for_analysis(db)
        
        if users_data.empty:
            raise HTTPException(status_code=400, detail="No user data available for analysis")
        
        # Perform RFM analysis
        if request.method in ["rfm", "hybrid"]:
            users_data = segmentation_engine.calculate_rfm_scores(users_data)
        
        # Perform clustering
        if request.method in ["clustering", "hybrid"]:
            users_data = segmentation_engine.perform_clustering(
                users_data, 
                method=request.clustering_method or "kmeans"
            )
        
        # Predict churn
        if request.include_churn_prediction:
            users_data = segmentation_engine.predict_churn(users_data)
        
        # Create segments
        segments = segmentation_engine.create_segments(users_data)
        
        # Store segments in database (background task)
        if segments:
            background_tasks.add_task(
                store_segments_in_database,
                db=db,
                segments=segments,
                users_data=users_data
            )
        
        # Prepare response
        analysis_summary = {
            "rfm_scores_calculated": "rfm" in request.method or "hybrid" in request.method,
            "clustering_performed": "clustering" in request.method or "hybrid" in request.method,
            "churn_prediction_completed": request.include_churn_prediction,
            "total_users": len(users_data),
            "segments_created": len(segments)
        }
        
        return SegmentationAnalysisResponse(
            segments_created=len(segments),
            total_users_analyzed=len(users_data),
            rfm_scores_calculated=analysis_summary["rfm_scores_calculated"],
            clustering_performed=analysis_summary["clustering_performed"],
            churn_prediction_completed=analysis_summary["churn_prediction_completed"],
            segments=[],  # Would convert segments to response models
            analysis_summary=analysis_summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Customer segmentation analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/users/{user_id}/recommendations", response_model=UserRecommendationResponse)
async def get_user_recommendations(
    user_id: int,
    db: AsyncSession = get_db
):
    """
    Get personalized recommendations for a specific user.
    
    Provides actionable insights and recommendations based on user's segment and behavior.
    """
    try:
        # Get user data
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get recommendations from segmentation engine
        # This would require getting all users data for context
        recommendations = {
            "user_id": user_id,
            "current_segment": "Unknown",  # Would get from user_segments table
            "churn_risk": "unknown",
            "recommendations": [],
            "next_best_actions": []
        }
        
        return UserRecommendationResponse(**recommendations)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.get("/rfm/scores")
async def get_rfm_scores(
    db: AsyncSession = get_db,
    user_id: Optional[int] = Query(None, description="Get RFM scores for specific user"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return")
):
    """
    Get RFM scores for users.
    
    Returns Recency, Frequency, and Monetary scores for customer analysis.
    """
    try:
        if user_id:
            # Get specific user's RFM scores
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Calculate RFM scores for single user
            user_data = pd.DataFrame([{
                'id': user.id,
                'last_activity': user.last_activity,
                'total_bets': user.total_bets,
                'lifetime_value': user.lifetime_value
            }])
            
            rfm_data = segmentation_engine.calculate_rfm_scores(user_data)
            return rfm_data.to_dict('records')[0]
        
        else:
            # Get RFM scores for multiple users
            result = await db.execute(
                select(User).limit(limit)
            )
            users = result.scalars().all()
            
            # Convert to DataFrame for analysis
            users_data = pd.DataFrame([{
                'id': user.id,
                'last_activity': user.last_activity,
                'total_bets': user.total_bets,
                'lifetime_value': user.lifetime_value
            } for user in users])
            
            rfm_data = segmentation_engine.calculate_rfm_scores(users_data)
            return rfm_data.to_dict('records')
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get RFM scores: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get RFM scores: {str(e)}")


@router.get("/churn/predictions")
async def get_churn_predictions(
    db: AsyncSession = get_db,
    risk_level: Optional[str] = Query(None, description="Filter by churn risk level"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return")
):
    """
    Get churn predictions for users.
    
    Returns churn probability and risk levels for customer retention analysis.
    """
    try:
        query = select(User).where(User.churn_probability.is_not(None))
        
        if risk_level:
            query = query.where(User.churn_risk_level == risk_level)
        
        query = query.limit(limit)
        
        result = await db.execute(query)
        users = result.scalars().all()
        
        churn_data = [{
            'user_id': user.id,
            'username': user.username,
            'churn_probability': user.churn_probability,
            'churn_risk_level': user.churn_risk_level,
            'lifetime_value': user.lifetime_value,
            'last_activity': user.last_activity
        } for user in users]
        
        return {
            'total_users': len(churn_data),
            'risk_distribution': {
                'low': len([u for u in churn_data if u['churn_risk_level'] == 'low']),
                'medium': len([u for u in churn_data if u['churn_risk_level'] == 'medium']),
                'high': len([u for u in churn_data if u['churn_risk_level'] == 'high'])
            },
            'users': churn_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get churn predictions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get churn predictions: {str(e)}")


@router.get("/engine/status")
async def get_segmentation_engine_status():
    """
    Get status of the customer segmentation engine.
    
    Provides information about model availability and configuration.
    """
    try:
        return segmentation_engine.get_engine_status()
    except Exception as e:
        logger.error(f"Failed to get engine status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get engine status: {str(e)}")


async def get_users_data_for_analysis(db: AsyncSession) -> pd.DataFrame:
    """Get user data for segmentation analysis"""
    try:
        result = await db.execute(
            select(User).where(User.status == UserStatus.ACTIVE)
        )
        users = result.scalars().all()
        
        # Convert to DataFrame
        users_data = pd.DataFrame([{
            'id': user.id,
            'last_activity': user.last_activity or user.created_at,
            'total_bets': user.total_bets,
            'lifetime_value': user.lifetime_value,
            'win_rate': user.win_rate,
            'average_bet_size': user.average_bet_size,
            'recency_score': user.recency_score,
            'frequency_score': user.frequency_score,
            'monetary_score': user.monetary_score
        } for user in users])
        
        return users_data
        
    except Exception as e:
        logger.error(f"Failed to get users data: {e}")
        return pd.DataFrame()


async def store_segments_in_database(
    db: AsyncSession,
    segments: Dict[str, Any],
    users_data: pd.DataFrame
):
    """Store segmentation results in database (background task)"""
    try:
        # This would implement the logic to store segments and user assignments
        # For now, just log the action
        logger.info(f"Storing {len(segments)} segments in database")
        
    except Exception as e:
        logger.error(f"Failed to store segments in database: {e}")
        await db.rollback()
