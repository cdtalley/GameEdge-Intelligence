from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
import os


class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str
    DATABASE_SYNC_URL: str
    
    # Security
    SECRET_KEY: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML Model Configuration
    ML_MODEL_PATH: str = "./models"
    SENTIMENT_MODEL_NAME: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    CACHE_MODELS: bool = True
    
    # Data Pipeline Configuration
    DATA_DIR: str = "./data"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GameEdge Intelligence"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Development
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # External APIs
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = None
    
    # Monitoring
    ENABLE_METRICS: bool = True
    PROMETHEUS_PORT: int = 9090
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Ensure ML model directory exists
os.makedirs(settings.ML_MODEL_PATH, exist_ok=True)
