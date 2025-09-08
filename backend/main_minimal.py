"""
Minimal FastAPI Application for GameEdge Intelligence Platform

This is the most minimal version possible to get the server running.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

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

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "GameEdge Intelligence API",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to GameEdge Intelligence API",
        "description": "Advanced Sports Betting Analytics Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Test endpoint
@app.get("/test")
async def test():
    """Test endpoint"""
    return {"message": "API is working!"}

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
