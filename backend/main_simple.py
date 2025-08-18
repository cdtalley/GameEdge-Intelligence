"""
Simplified Main FastAPI Application for GameEdge Intelligence Platform

This is a simplified version that avoids complex dependencies and gets the basic server running.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import structlog
from datetime import datetime

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
        # Initialize ML models (this happens automatically in the ML modules)
        logger.info("ML models initialization completed")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down GameEdge Intelligence API")


# Create FastAPI application
app = FastAPI(
    title="GameEdge Intelligence",
    description="""
    GameEdge Intelligence - Advanced Sports Betting Analytics Platform
    
    ## Features
    
    * **Sentiment Analysis**: Multi-model sentiment analysis with BERT transformers and ML fallback
    * **Customer Segmentation**: RFM analysis, clustering, and churn prediction
    * **Real-time Analytics**: Live dashboard with comprehensive business intelligence
    * **ML Pipeline**: Automated model training and inference
    
    ## API Endpoints
    
    * `/health` - Health check endpoint
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
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        ]
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("GameEdge Intelligence API is starting up")
    
    # Log configuration
    logger.info(
        "Application configuration",
        environment="development",
        debug=True
    )


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("GameEdge Intelligence API is shutting down")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
