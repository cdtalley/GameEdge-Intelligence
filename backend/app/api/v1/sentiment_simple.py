"""
Simplified Sentiment Analysis API for GameEdge Intelligence Platform

This is a simplified version that avoids complex dependencies and enum issues.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from ...core.database import get_db
from ...ml.sentiment_analyzer import sentiment_analyzer

logger = logging.getLogger(__name__)

router = APIRouter()


class SentimentAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="Text to analyze")
    user_id: Optional[int] = Field(None, description="User ID for context")


class SentimentAnalysisResponse(BaseModel):
    sentiment_label: str
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


@router.post("/analyze", response_model=SentimentAnalysisResponse)
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze sentiment of a single text input.
    """
    try:
        # Perform sentiment analysis
        result = sentiment_analyzer.analyze_sentiment(
            text=request.text,
            user_id=request.user_id
        )
        
        return SentimentAnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")


@router.post("/analyze/batch", response_model=BatchSentimentResponse)
async def analyze_sentiment_batch(
    request: BatchSentimentRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze sentiment of multiple texts in batch.
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
                    "sentiment_label": "neutral",
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


@router.get("/model/status")
async def get_model_status():
    """
    Get detailed status of sentiment analysis models.
    """
    try:
        return sentiment_analyzer.get_model_status()
    except Exception as e:
        logger.error(f"Failed to get model status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")


@router.get("/aspects")
async def get_supported_aspects():
    """
    Get list of supported sentiment aspects for sports betting context.
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
