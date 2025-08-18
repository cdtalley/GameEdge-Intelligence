from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from ...core.database import get_db
from ...ml.sentiment_analyzer import sentiment_analyzer
from ...models import Interaction, User
from enum import Enum

# Pydantic enums for API responses
class SentimentLabelAPI(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

class InteractionTypeAPI(str, Enum):
    REVIEW = "review"
    FEEDBACK = "feedback"
    SUPPORT_TICKET = "support_ticket"
    SOCIAL_MEDIA = "social_media"
    APP_REVIEW = "app_review"
    BET_COMMENT = "bet_comment"
    GENERAL = "general"

logger = logging.getLogger(__name__)

router = APIRouter()


class SentimentAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="Text to analyze")
    user_id: Optional[int] = Field(None, description="User ID for context")
    interaction_type: Optional[InteractionTypeAPI] = Field(None, description="Type of interaction")
    source: Optional[str] = Field("api", description="Source of the text")
    related_bet_id: Optional[int] = Field(None, description="Related bet ID if applicable")
    sport: Optional[str] = Field(None, description="Sport context")
    team: Optional[str] = Field(None, description="Team context")
    event: Optional[str] = Field(None, description="Event context")
    language: Optional[str] = Field("en", description="Language of the text")
    is_public: Optional[bool] = Field(True, description="Whether the interaction is public")


class SentimentAnalysisResponse(BaseModel):
    sentiment_label: SentimentLabelAPI
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    aspects: Dict[str, float]
    model_used: str
    user_id: Optional[int]
    text: str
    processed_text: str
    timestamp: str
    model_info: Dict[str, Any]
    error: Optional[str] = None


class BatchSentimentRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=100)
    user_id: Optional[int] = Field(None, description="User ID for context")


class BatchSentimentResponse(BaseModel):
    results: List[SentimentAnalysisResponse]
    total_processed: int
    successful: int
    failed: int


class SentimentStatsResponse(BaseModel):
    total_interactions: int
    sentiment_distribution: Dict[str, int]
    average_confidence: float
    model_status: Dict[str, Any]
    recent_trends: List[Dict[str, Any]]


@router.post("/analyze", response_model=SentimentAnalysisResponse)
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = get_db
):
    """
    Analyze sentiment of a single text input.
    
    This endpoint provides comprehensive sentiment analysis using our multi-model approach:
    - BERT-based transformer model for primary analysis
    - Traditional ML fallback for reliability
    - Aspect-based sentiment extraction for sports betting context
    """
    try:
        # Perform sentiment analysis
        result = sentiment_analyzer.analyze_sentiment(
            text=request.text,
            user_id=request.user_id
        )
        
        # Store interaction in database if user_id is provided
        if request.user_id:
            background_tasks.add_task(
                store_interaction,
                db=db,
                request=request,
                result=result
            )
        
        return SentimentAnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")


@router.post("/analyze/batch", response_model=BatchSentimentResponse)
async def analyze_sentiment_batch(
    request: BatchSentimentRequest,
    db: AsyncSession = get_db
):
    """
    Analyze sentiment of multiple texts in batch.
    
    This is optimized for processing large volumes of text data efficiently.
    """
    try:
        results = []
        successful = 0
        failed = 0
        
        for text in request.texts:
            try:
                result = sentiment_analyzer.analyze_sentiment(
                    text=text,
                    user_id=request.user_id
                )
                results.append(SentimentAnalysisResponse(**result))
                successful += 1
            except Exception as e:
                logger.error(f"Failed to analyze text: {e}")
                # Create error response for failed analysis
                error_result = {
                    "sentiment_label": SentimentLabelAPI.NEUTRAL,
                    "sentiment_score": 0.0,
                    "confidence_score": 0.0,
                    "aspects": {},
                    "model_used": "error",
                    "user_id": request.user_id,
                    "text": text,
                    "processed_text": text,
                    "timestamp": "",
                    "model_info": {},
                    "error": str(e)
                }
                results.append(SentimentAnalysisResponse(**error_result))
                failed += 1
        
        return BatchSentimentResponse(
            results=results,
            total_processed=len(request.texts),
            successful=successful,
            failed=failed
        )
        
    except Exception as e:
        logger.error(f"Batch sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@router.get("/stats", response_model=SentimentStatsResponse)
async def get_sentiment_stats(db: AsyncSession = get_db):
    """
    Get sentiment analysis statistics and trends.
    
    Provides comprehensive overview of sentiment analysis performance and usage.
    """
    try:
        # Get model status
        model_status = sentiment_analyzer.get_model_status()
        
        # Get basic stats from database
        # Note: In production, this would use more sophisticated analytics
        stats = {
            "total_interactions": 0,  # Would query database
            "sentiment_distribution": {
                "positive": 0,
                "negative": 0,
                "neutral": 0
            },
            "average_confidence": 0.0,
            "model_status": model_status,
            "recent_trends": []
        }
        
        return SentimentStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Failed to get sentiment stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/model/status")
async def get_model_status():
    """
    Get detailed status of sentiment analysis models.
    
    Provides information about model availability, performance, and configuration.
    """
    try:
        return sentiment_analyzer.get_model_status()
    except Exception as e:
        logger.error(f"Failed to get model status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")


@router.post("/model/reload")
async def reload_models():
    """
    Reload sentiment analysis models.
    
    Useful for updating models or recovering from errors.
    """
    try:
        result = sentiment_analyzer.reload_models()
        return {"message": "Models reloaded successfully", "status": result}
    except Exception as e:
        logger.error(f"Failed to reload models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reload models: {str(e)}")


@router.get("/aspects")
async def get_supported_aspects():
    """
    Get list of supported sentiment aspects for sports betting context.
    
    Returns the aspects that can be analyzed in text, such as odds, customer service, etc.
    """
    try:
        return {
            "sports_aspects": sentiment_analyzer.sports_aspects,
            "sports_terms": sentiment_analyzer.sports_terms,
            "description": "Supported aspects and terms for sports betting sentiment analysis"
        }
    except Exception as e:
        logger.error(f"Failed to get supported aspects: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get aspects: {str(e)}")


async def store_interaction(
    db: AsyncSession,
    request: SentimentAnalysisRequest,
    result: Dict[str, Any]
):
    """
    Store interaction in database (background task).
    
    This function runs asynchronously to avoid blocking the API response.
    """
    try:
        # Convert API enums to SQLAlchemy enums
        from ...models import SentimentLabel, InteractionType
        
        # Create new interaction record
        interaction = Interaction(
            user_id=request.user_id,
            interaction_type=request.interaction_type.value if request.interaction_type else InteractionType.GENERAL,
            title=f"Sentiment Analysis - {result.get('sentiment_label', 'unknown')}",
            content=request.text,
            source=request.source,
            sentiment_label=result.get('sentiment_label').value if result.get('sentiment_label') else None,
            sentiment_score=result.get('sentiment_score'),
            confidence_score=result.get('confidence_score'),
            aspects=result.get('aspects', {}),
            model_used=result.get('model_used'),
            model_version="1.0",  # Would come from model info
            related_bet_id=request.related_bet_id,
            sport=request.sport,
            team=request.team,
            event=request.event,
            language=request.language,
            is_public=request.is_public,
            processed_at=result.get('timestamp')
        )
        
        db.add(interaction)
        await db.commit()
        
        logger.info(f"Stored interaction for user {request.user_id}")
        
    except Exception as e:
        logger.error(f"Failed to store interaction: {e}")
        await db.rollback()
