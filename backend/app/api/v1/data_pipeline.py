"""
Data Pipeline API endpoints for GameEdge Intelligence Platform

Provides endpoints for:
- Running the full data pipeline
- Generating synthetic data
- Managing dataset operations
- Data cleanup and maintenance
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Optional
import logging

from ...core.database import get_db
from ...core.data_pipeline import data_pipeline
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()

class DataPipelineRequest:
    """Request model for data pipeline operations"""
    kaggle_token: Optional[str] = None
    num_users: Optional[int] = 1000
    force_download: bool = False

class DataPipelineResponse:
    """Response model for data pipeline operations"""
    success: bool
    message: str
    results: Optional[Dict] = None
    error: Optional[str] = None

@router.post("/pipeline/run", response_model=DataPipelineResponse)
async def run_data_pipeline(
    request: DataPipelineRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Run the complete data pipeline to download and transform datasets
    
    This endpoint will:
    1. Download the three primary datasets from Kaggle
    2. Transform them into betting-related data
    3. Load the data into the database
    """
    try:
        if not request.kaggle_token:
            raise HTTPException(
                status_code=400, 
                detail="Kaggle token is required for dataset download"
            )
        
        # Run pipeline in background to avoid timeout
        background_tasks.add_task(
            data_pipeline.run_full_pipeline, 
            db, 
            request.kaggle_token
        )
        
        return DataPipelineResponse(
            success=True,
            message="Data pipeline started in background. Check logs for progress.",
            results={"status": "running"}
        )
        
    except Exception as e:
        logger.error(f"Error starting data pipeline: {str(e)}")
        return DataPipelineResponse(
            success=False,
            message="Failed to start data pipeline",
            error=str(e)
        )

@router.post("/pipeline/synthetic", response_model=DataPipelineResponse)
async def generate_synthetic_data(
    request: DataPipelineRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate synthetic data for testing and development
    
    Creates realistic betting data including:
    - Users with various profiles and behaviors
    - Betting transactions across different sports
    - Customer interactions and reviews
    """
    try:
        results = await data_pipeline.generate_synthetic_data(
            db, 
            request.num_users
        )
        
        return DataPipelineResponse(
            success=True,
            message=f"Successfully generated synthetic data for {request.num_users} users",
            results=results
        )
        
    except Exception as e:
        logger.error(f"Error generating synthetic data: {str(e)}")
        return DataPipelineResponse(
            success=False,
            message="Failed to generate synthetic data",
            error=str(e)
        )

@router.post("/pipeline/cleanup", response_model=DataPipelineResponse)
async def cleanup_data(
    db: AsyncSession = Depends(get_db)
):
    """
    Clean up all data from the database
    
    WARNING: This will delete all users, bets, interactions, and segments.
    Use with caution in production environments.
    """
    try:
        success = await data_pipeline.cleanup_data(db)
        
        if success:
            return DataPipelineResponse(
                success=True,
                message="Data cleanup completed successfully",
                results={"status": "cleaned"}
            )
        else:
            return DataPipelineResponse(
                success=False,
                message="Data cleanup failed",
                error="Database operation failed"
            )
        
    except Exception as e:
        logger.error(f"Error during data cleanup: {str(e)}")
        return DataPipelineResponse(
            success=False,
            message="Failed to cleanup data",
            error=str(e)
        )

@router.get("/pipeline/status")
async def get_pipeline_status():
    """
    Get the current status of the data pipeline
    
    Returns information about:
    - Available datasets
    - Download status
    - Transformation progress
    """
    try:
        # Check which datasets exist locally
        status = {}
        for dataset_name, dataset_info in data_pipeline.datasets.items():
            file_path = data_pipeline.data_dir / dataset_info["filename"]
            status[dataset_name] = {
                "name": dataset_name,
                "description": dataset_info["description"],
                "size_mb": dataset_info["size_mb"],
                "downloaded": file_path.exists(),
                "file_size": file_path.stat().st_size if file_path.exists() else 0
            }
        
        return {
            "success": True,
            "data_dir": str(data_pipeline.data_dir),
            "datasets": status,
            "total_size_mb": sum(info["size_mb"] for info in data_pipeline.datasets.values())
        }
        
    except Exception as e:
        logger.error(f"Error getting pipeline status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pipeline status: {str(e)}"
        )

@router.post("/pipeline/download/{dataset_name}")
async def download_specific_dataset(
    dataset_name: str,
    request: DataPipelineRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Download a specific dataset by name
    
    Available datasets:
    - sentiment140: Twitter sentiment analysis
    - online_retail: Customer behavior data
    - football_odds: Sports betting odds
    """
    try:
        if not request.kaggle_token:
            raise HTTPException(
                status_code=400,
                detail="Kaggle token is required for dataset download"
            )
        
        if dataset_name not in data_pipeline.datasets:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown dataset: {dataset_name}. Available: {list(data_pipeline.datasets.keys())}"
            )
        
        success = await data_pipeline.download_dataset(dataset_name, request.kaggle_token)
        
        if success:
            return DataPipelineResponse(
                success=True,
                message=f"Successfully downloaded {dataset_name}",
                results={"dataset": dataset_name, "status": "downloaded"}
            )
        else:
            return DataPipelineResponse(
                success=False,
                message=f"Failed to download {dataset_name}",
                error="Download operation failed"
            )
        
    except Exception as e:
        logger.error(f"Error downloading dataset {dataset_name}: {str(e)}")
        return DataPipelineResponse(
            success=False,
            message=f"Failed to download {dataset_name}",
            error=str(e)
        )

@router.post("/pipeline/transform/{dataset_name}")
async def transform_specific_dataset(
    dataset_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Transform a specific dataset and load it into the database
    
    This will process the downloaded dataset and create:
    - Users (from customer data)
    - Bets (from transactions)
    - Interactions (from reviews/sentiment)
    """
    try:
        if dataset_name == "sentiment140":
            count = await data_pipeline.transform_sentiment140(db)
            message = f"Transformed {count} sentiment interactions"
        elif dataset_name == "online_retail":
            count = await data_pipeline.transform_online_retail(db)
            message = f"Transformed {count} retail records into users and bets"
        elif dataset_name == "football_odds":
            count = await data_pipeline.transform_football_odds(db)
            message = f"Transformed {count} football odds into bets"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown dataset: {dataset_name}"
            )
        
        return DataPipelineResponse(
            success=True,
            message=message,
            results={"dataset": dataset_name, "records_processed": count}
        )
        
    except Exception as e:
        logger.error(f"Error transforming dataset {dataset_name}: {str(e)}")
        return DataPipelineResponse(
            success=False,
            message=f"Failed to transform {dataset_name}",
            error=str(e)
        )

@router.get("/pipeline/info")
async def get_pipeline_info():
    """
    Get detailed information about the data pipeline
    
    Returns:
    - Available datasets and their descriptions
    - Sports and bet type mappings
    - Configuration information
    """
    try:
        return {
            "success": True,
            "data_pipeline": {
                "data_directory": str(data_pipeline.data_dir),
                "available_datasets": data_pipeline.datasets,
                "sports_mapping": data_pipeline.sports_mapping,
                "bet_types": data_pipeline.bet_types,
                "description": "GameEdge Intelligence Data Pipeline for transforming retail and sentiment data into sports betting analytics"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting pipeline info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pipeline info: {str(e)}"
        )
