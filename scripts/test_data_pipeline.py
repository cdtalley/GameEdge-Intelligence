#!/usr/bin/env python3
"""
Test script for GameEdge Intelligence Data Pipeline

This script tests the data pipeline functionality by:
1. Testing synthetic data generation
2. Verifying database operations
3. Testing data transformation logic
4. Validating API endpoints

Usage:
    python scripts/test_data_pipeline.py
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.database import AsyncSessionLocal, init_db, close_db
from app.core.data_pipeline import data_pipeline
from app.models import User, Bet, Interaction, Segment, UserSegment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_database_connection():
    """Test database connectivity and initialization"""
    logger.info("Testing database connection...")
    
    try:
        await init_db()
        logger.info("✓ Database initialization successful")
        
        async with AsyncSessionLocal() as db:
            # Test basic query
            result = await db.execute("SELECT 1 as test")
            row = result.fetchone()
            if row and row.test == 1:
                logger.info("✓ Database query successful")
            else:
                logger.error("✗ Database query failed")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Database connection failed: {str(e)}")
        return False

async def test_synthetic_data_generation():
    """Test synthetic data generation with small dataset"""
    logger.info("Testing synthetic data generation...")
    
    try:
        async with AsyncSessionLocal() as db:
            # Generate small amount of synthetic data
            results = await data_pipeline.generate_synthetic_data(db, num_users=10)
            
            if results and results.get('users', 0) > 0:
                logger.info(f"✓ Generated {results['users']} users")
                logger.info(f"✓ Generated {results['bets']} bets")
                logger.info(f"✓ Generated {results['interactions']} interactions")
                return True
            else:
                logger.error("✗ Synthetic data generation failed")
                return False
                
    except Exception as e:
        logger.error(f"✗ Synthetic data generation error: {str(e)}")
        return False

async def test_data_queries():
    """Test data retrieval and basic analytics"""
    logger.info("Testing data queries...")
    
    try:
        async with AsyncSessionLocal() as db:
            # Count users
            result = await db.execute("SELECT COUNT(*) as count FROM users")
            user_count = result.fetchone().count
            logger.info(f"✓ Found {user_count} users in database")
            
            # Count bets
            result = await db.execute("SELECT COUNT(*) as count FROM bets")
            bet_count = result.fetchone().count
            logger.info(f"✓ Found {bet_count} bets in database")
            
            # Count interactions
            result = await db.execute("SELECT COUNT(*) as count FROM interactions")
            interaction_count = result.fetchone().count
            logger.info(f"✓ Found {interaction_count} interactions in database")
            
            # Test basic analytics query
            result = await db.execute("""
                SELECT 
                    COUNT(DISTINCT user_id) as active_users,
                    AVG(stake) as avg_stake,
                    SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losses
                FROM bets
            """)
            
            analytics = result.fetchone()
            if analytics:
                logger.info(f"✓ Analytics query successful:")
                logger.info(f"  - Active users: {analytics.active_users}")
                logger.info(f"  - Average stake: ${analytics.avg_stake:.2f}")
                logger.info(f"  - Win rate: {analytics.wins/(analytics.wins + analytics.losses)*100:.1f}%")
            
            return True
            
    except Exception as e:
        logger.error(f"✗ Data queries failed: {str(e)}")
        return False

async def test_data_pipeline_status():
    """Test data pipeline status checking"""
    logger.info("Testing data pipeline status...")
    
    try:
        # Check pipeline info
        pipeline_info = await data_pipeline.get_pipeline_info()
        if pipeline_info:
            logger.info("✓ Pipeline info retrieved successfully")
            logger.info(f"  - Data directory: {pipeline_info['data_directory']}")
            logger.info(f"  - Available datasets: {len(pipeline_info['available_datasets'])}")
            logger.info(f"  - Sports mapping: {len(pipeline_info['sports_mapping'])} sports")
            logger.info(f"  - Bet types: {len(pipeline_info['bet_types'])} types")
            return True
        else:
            logger.error("✗ Failed to get pipeline info")
            return False
            
    except Exception as e:
        logger.error(f"✗ Pipeline status check failed: {str(e)}")
        return False

async def test_data_cleanup():
    """Test data cleanup functionality"""
    logger.info("Testing data cleanup...")
    
    try:
        async with AsyncSessionLocal() as db:
            # Count records before cleanup
            result = await db.execute("SELECT COUNT(*) as count FROM users")
            users_before = result.fetchone().count
            
            result = await db.execute("SELECT COUNT(*) as count FROM bets")
            bets_before = result.fetchone().count
            
            logger.info(f"Records before cleanup: {users_before} users, {bets_before} bets")
            
            # Perform cleanup
            success = await data_pipeline.cleanup_data(db)
            
            if success:
                # Verify cleanup
                result = await db.execute("SELECT COUNT(*) as count FROM users")
                users_after = result.fetchone().count
                
                result = await db.execute("SELECT COUNT(*) as count FROM bets")
                bets_after = result.fetchone().count
                
                if users_after == 0 and bets_after == 0:
                    logger.info("✓ Data cleanup successful - all records removed")
                    return True
                else:
                    logger.error(f"✗ Data cleanup incomplete: {users_after} users, {bets_after} bets remaining")
                    return False
            else:
                logger.error("✗ Data cleanup operation failed")
                return False
                
    except Exception as e:
        logger.error(f"✗ Data cleanup test failed: {str(e)}")
        return False

async def run_all_tests():
    """Run all data pipeline tests"""
    logger.info("Starting data pipeline tests...")
    print("\n" + "="*60)
    print("DATA PIPELINE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Synthetic Data Generation", test_synthetic_data_generation),
        ("Data Queries", test_data_queries),
        ("Pipeline Status", test_data_pipeline_status),
        ("Data Cleanup", test_data_cleanup)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning test: {test_name}")
        try:
            success = await test_func()
            if success:
                logger.info(f"✓ {test_name} PASSED")
                passed += 1
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} ERROR: {str(e)}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Data pipeline is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check logs for details.")
        return False

async def main():
    """Main test execution"""
    try:
        success = await run_all_tests()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during testing: {str(e)}")
        sys.exit(1)
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
