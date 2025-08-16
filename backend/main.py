from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import structlog
from datetime import datetime

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1 import sentiment, customers, analytics, data_pipeline

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting GameEdge Intelligence API")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Initialize ML models (this happens automatically in the ML modules)
        logger.info("ML models initialization completed")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down GameEdge Intelligence API")
    try:
        await close_db()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    GameEdge Intelligence - Advanced Sports Betting Analytics Platform
    
    ## Features
    
    * **Sentiment Analysis**: Multi-model sentiment analysis with BERT transformers and ML fallback
    * **Customer Segmentation**: RFM analysis, clustering, and churn prediction
    * **Real-time Analytics**: Live dashboard with comprehensive business intelligence
    * **ML Pipeline**: Automated model training and inference
    
    ## Datasets
    
    * 1.6M+ pre-labeled tweets for sentiment analysis
    * 525K+ transaction records for customer behavior modeling
    * 500K+ sports matches with comprehensive odds data
    * 50K+ synthetic customer profiles with realistic demographics
    
    ## API Endpoints
    
    * `/api/v1/sentiment/*` - Sentiment analysis endpoints
    * `/api/v1/customers/*` - Customer segmentation and analytics
    * `/api/v1/analytics/*` - Business intelligence and reporting
    * `/docs` - Interactive API documentation
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # In production, restrict to specific domains
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        path=request.url.path,
        method=request.method,
        client_ip=request.client.host if request.client else None
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )


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
        ],
        "dataset_scale": {
            "sentiment_tweets": "1.6M+",
            "transaction_records": "525K+",
            "sports_matches": "500K+",
            "customer_profiles": "50K+"
        }
    }


# Include API routers
app.include_router(
    sentiment.router,
    prefix=f"{settings.API_V1_STR}/sentiment",
    tags=["sentiment-analysis"]
)

app.include_router(
    customers.router,
    prefix=f"{settings.API_V1_STR}/customers",
    tags=["customer-segmentation"]
)

app.include_router(
    analytics.router,
    prefix=f"{settings.API_V1_STR}/analytics",
    tags=["analytics-dashboard"]
)

app.include_router(
    data_pipeline.router,
    prefix=f"{settings.API_V1_STR}/data-pipeline",
    tags=["data-pipeline"]
)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("GameEdge Intelligence API is starting up")
    
    # Log configuration
    logger.info(
        "Application configuration",
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG,
        database_url=settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "configured",
        ml_model_path=settings.ML_MODEL_PATH,
        cors_origins=settings.BACKEND_CORS_ORIGINS
    )


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("GameEdge Intelligence API is shutting down")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
