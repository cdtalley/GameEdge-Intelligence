#!/usr/bin/env python3
"""
Data Pipeline Management Script for GameEdge Intelligence

This script provides a command-line interface for managing the data pipeline:
- Downloading datasets from Kaggle
- Transforming and loading data
- Generating synthetic data
- Monitoring pipeline status

Usage:
    python scripts/manage_data_pipeline.py [command] [options]

Commands:
    download    Download datasets from Kaggle
    transform   Transform downloaded datasets
    synthetic   Generate synthetic data
    status      Check pipeline status
    cleanup     Clean up all data
    run-all     Run complete pipeline
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
import logging

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.database import AsyncSessionLocal, init_db, close_db
from app.core.data_pipeline import data_pipeline
from app.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def download_datasets(kaggle_token: str, dataset_names: list = None):
    """Download specified datasets from Kaggle"""
    if not kaggle_token:
        logger.error("Kaggle token is required for dataset download")
        return False
    
    if not dataset_names:
        dataset_names = list(data_pipeline.datasets.keys())
    
    logger.info(f"Starting download of datasets: {', '.join(dataset_names)}")
    
    success_count = 0
    for dataset_name in dataset_names:
        if dataset_name in data_pipeline.datasets:
            logger.info(f"Downloading {dataset_name}...")
            success = await data_pipeline.download_dataset(dataset_name, kaggle_token)
            if success:
                success_count += 1
                logger.info(f"✓ Successfully downloaded {dataset_name}")
            else:
                logger.error(f"✗ Failed to download {dataset_name}")
        else:
            logger.warning(f"Unknown dataset: {dataset_name}")
    
    logger.info(f"Download completed: {success_count}/{len(dataset_names)} datasets successful")
    return success_count == len(dataset_names)

async def transform_datasets(dataset_names: list = None):
    """Transform downloaded datasets into betting data"""
    if not dataset_names:
        dataset_names = list(data_pipeline.datasets.keys())
    
    logger.info(f"Starting transformation of datasets: {', '.join(dataset_names)}")
    
    async with AsyncSessionLocal() as db:
        total_records = 0
        
        for dataset_name in dataset_names:
            if dataset_name == "sentiment140":
                count = await data_pipeline.transform_sentiment140(db)
                logger.info(f"✓ Transformed {count} sentiment interactions")
                total_records += count
            elif dataset_name == "online_retail":
                count = await data_pipeline.transform_online_retail(db)
                logger.info(f"✓ Transformed {count} retail records")
                total_records += count
            elif dataset_name == "football_odds":
                count = await data_pipeline.transform_football_odds(db)
                logger.info(f"✓ Transformed {count} football odds")
                total_records += count
            else:
                logger.warning(f"Unknown dataset: {dataset_name}")
        
        logger.info(f"Transformation completed: {total_records} total records processed")
        return total_records

async def generate_synthetic_data(num_users: int = 1000):
    """Generate synthetic data for testing"""
    logger.info(f"Generating synthetic data for {num_users} users...")
    
    async with AsyncSessionLocal() as db:
        results = await data_pipeline.generate_synthetic_data(db, num_users)
        
        if results:
            logger.info(f"✓ Generated {results.get('users', 0)} users")
            logger.info(f"✓ Generated {results.get('bets', 0)} bets")
            logger.info(f"✓ Generated {results.get('interactions', 0)} interactions")
            return True
        else:
            logger.error("✗ Failed to generate synthetic data")
            return False

async def check_pipeline_status():
    """Check the current status of the data pipeline"""
    logger.info("Checking pipeline status...")
    
    try:
        # Check which datasets exist locally
        status = {}
        for dataset_name, dataset_info in data_pipeline.datasets.items():
            file_path = data_pipeline.data_dir / dataset_info["filename"]
            exists = file_path.exists()
            file_size = file_path.stat().st_size if exists else 0
            
            status[dataset_name] = {
                "downloaded": exists,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "expected_size_mb": dataset_info["size_mb"],
                "description": dataset_info["description"]
            }
        
        # Display status
        print("\n" + "="*60)
        print("DATA PIPELINE STATUS")
        print("="*60)
        
        for dataset_name, info in status.items():
            status_icon = "✓" if info["downloaded"] else "✗"
            print(f"{status_icon} {dataset_name.upper()}")
            print(f"   Description: {info['description']}")
            print(f"   Status: {'Downloaded' if info['downloaded'] else 'Not downloaded'}")
            if info["downloaded"]:
                print(f"   File size: {info['file_size_mb']} MB (expected: {info['expected_size_mb']} MB)")
            print()
        
        total_downloaded = sum(1 for info in status.values() if info["downloaded"])
        total_expected = len(status)
        
        print(f"Overall Status: {total_downloaded}/{total_expected} datasets downloaded")
        print(f"Data directory: {data_pipeline.data_dir}")
        print("="*60)
        
        return status
        
    except Exception as e:
        logger.error(f"Error checking pipeline status: {str(e)}")
        return None

async def cleanup_all_data():
    """Clean up all data from the database"""
    logger.warning("This will delete ALL data from the database!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        logger.info("Cleanup cancelled")
        return False
    
    logger.info("Cleaning up all data...")
    
    async with AsyncSessionLocal() as db:
        success = await data_pipeline.cleanup_data(db)
        
        if success:
            logger.info("✓ Data cleanup completed successfully")
            return True
        else:
            logger.error("✗ Data cleanup failed")
            return False

async def run_complete_pipeline(kaggle_token: str):
    """Run the complete data pipeline"""
    logger.info("Starting complete data pipeline...")
    
    try:
        # Initialize database
        await init_db()
        
        # Download datasets
        download_success = await download_datasets(kaggle_token)
        if not download_success:
            logger.error("Dataset download failed, stopping pipeline")
            return False
        
        # Transform datasets
        transform_success = await transform_datasets()
        if transform_success == 0:
            logger.error("Dataset transformation failed, stopping pipeline")
            return False
        
        logger.info("✓ Complete data pipeline finished successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        return False
    finally:
        await close_db()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="GameEdge Intelligence Data Pipeline Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "command",
        choices=["download", "transform", "synthetic", "status", "cleanup", "run-all"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--kaggle-token",
        help="Kaggle API token (username:key format)"
    )
    
    parser.add_argument(
        "--datasets",
        nargs="+",
        choices=list(data_pipeline.datasets.keys()),
        help="Specific datasets to process"
    )
    
    parser.add_argument(
        "--num-users",
        type=int,
        default=1000,
        help="Number of synthetic users to generate (default: 1000)"
    )
    
    args = parser.parse_args()
    
    # Validate required arguments
    if args.command in ["download", "run-all"] and not args.kaggle_token:
        logger.error("Kaggle token is required for download and run-all commands")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == "download":
            success = asyncio.run(download_datasets(args.kaggle_token, args.datasets))
            sys.exit(0 if success else 1)
            
        elif args.command == "transform":
            records = asyncio.run(transform_datasets(args.datasets))
            sys.exit(0 if records > 0 else 1)
            
        elif args.command == "synthetic":
            success = asyncio.run(generate_synthetic_data(args.num_users))
            sys.exit(0 if success else 1)
            
        elif args.command == "status":
            asyncio.run(check_pipeline_status())
            sys.exit(0)
            
        elif args.command == "cleanup":
            success = asyncio.run(cleanup_all_data())
            sys.exit(0 if success else 1)
            
        elif args.command == "run-all":
            success = asyncio.run(run_complete_pipeline(args.kaggle_token))
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
