"""
Simplified Working FastAPI Backend for GameEdge Intelligence Platform

This version can run successfully without complex environment configuration.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="GameEdge Intelligence",
    description="Advanced Sports Betting Analytics Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data for demonstration
MOCK_DASHBOARD_DATA = {
    "metrics": {
        "total_users": 15420,
        "active_users": 8920,
        "total_bets": 45678,
        "total_revenue": 2345678.90,
        "average_bet_size": 51.40,
        "win_rate": 68.5,
        "sentiment_score": 0.72,
        "churn_risk": 0.23
    },
    "recent_activity": [
        {"id": 1, "type": "bet", "user": "JohnDoe", "action": "placed a bet", "amount": 100, "sport": "Football", "time": "2 min ago"},
        {"id": 2, "type": "withdrawal", "user": "BetMaster", "action": "withdrew", "amount": 500, "sport": "N/A", "time": "5 min ago"},
        {"id": 3, "type": "bet", "user": "SportsFan", "action": "won a bet", "amount": 250, "sport": "Basketball", "time": "8 min ago"}
    ],
    "top_sports": [
        {"sport": "Football", "bets": 12500, "revenue": 850000, "growth": 12.5},
        {"sport": "Basketball", "bets": 9800, "revenue": 650000, "growth": 8.3},
        {"sport": "Baseball", "bets": 7200, "revenue": 480000, "growth": 15.2}
    ],
    "sentiment_trends": [
        {"date": "2024-01-01", "positive": 65, "negative": 20, "neutral": 15},
        {"date": "2024-01-02", "positive": 70, "negative": 18, "neutral": 12},
        {"date": "2024-01-03", "positive": 68, "negative": 22, "neutral": 10}
    ]
}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "GameEdge Intelligence API",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to GameEdge Intelligence API",
        "description": "Advanced Sports Betting Analytics Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "Sentiment Analysis Engine",
            "Customer Segmentation System",
            "Real-time Analytics Dashboard",
            "Advanced ML Pipeline"
        ]
    }

# Dashboard data endpoint
@app.get("/api/v1/dashboard")
async def get_dashboard_data():
    """Get dashboard metrics and data"""
    try:
        return {
            "success": True,
            "data": MOCK_DASHBOARD_DATA,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

# Sentiment analysis endpoint
@app.post("/api/v1/sentiment/analyze")
async def analyze_sentiment(request: dict):
    """Analyze sentiment of text input"""
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Simple mock sentiment analysis
        # In production, this would use the actual ML models
        sentiment_score = 0.0
        if any(word in text.lower() for word in ["great", "amazing", "love", "excellent", "fantastic"]):
            sentiment_score = 0.8
        elif any(word in text.lower() for word in ["terrible", "awful", "hate", "bad", "worst"]):
            sentiment_score = -0.7
        else:
            sentiment_score = 0.1
        
        sentiment_label = "positive" if sentiment_score > 0.3 else "negative" if sentiment_score < -0.3 else "neutral"
        
        return {
            "success": True,
            "sentiment_label": sentiment_label,
            "sentiment_score": sentiment_score,
            "confidence_score": 0.85,
            "text": text,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze sentiment")

# Customer segments endpoint
@app.get("/api/v1/customers/segments")
async def get_customer_segments():
    """Get customer segmentation data"""
    try:
        segments = [
            {
                "id": 1,
                "name": "High Value Customers",
                "user_count": 1250,
                "avg_lifetime_value": 2500.0,
                "churn_risk": 0.15
            },
            {
                "id": 2,
                "name": "Active Bettors",
                "user_count": 3200,
                "avg_lifetime_value": 800.0,
                "churn_risk": 0.25
            },
            {
                "id": 3,
                "name": "At Risk Customers",
                "user_count": 890,
                "avg_lifetime_value": 150.0,
                "churn_risk": 0.75
            }
        ]
        
        return {
            "success": True,
            "segments": segments,
            "total_segments": len(segments),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting customer segments: {e}")
        raise HTTPException(status_code=500, detail="Failed to get customer segments")

# Analytics endpoint
@app.get("/api/v1/analytics/dashboard")
async def get_analytics_dashboard():
    """Get comprehensive analytics data"""
    try:
        return {
            "success": True,
            "data": MOCK_DASHBOARD_DATA,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting analytics data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics data")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main_simple_working:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

