#!/usr/bin/env python3
"""
Demo script for GameEdge Intelligence Data Pipeline

This script demonstrates the data pipeline capabilities by:
1. Setting up the environment
2. Generating synthetic data
3. Running basic analytics
4. Showing the transformation process

Usage:
    python scripts/demo_data_pipeline.py
"""

import asyncio
import sys
import logging
from pathlib import Path
import time

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.database import AsyncSessionLocal, init_db, close_db
from app.core.data_pipeline import data_pipeline
from app.models import User, Bet, Interaction

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n📋 {title}")
    print("-" * 40)

async def demo_setup():
    """Demo setup and initialization"""
    print_header("🎯 GAMEEDGE INTELLIGENCE DATA PIPELINE DEMO")
    
    print_section("Initializing Environment")
    
    try:
        # Initialize database
        await init_db()
        logger.info("✓ Database initialized successfully")
        
        # Check pipeline status
        pipeline_info = await data_pipeline.get_pipeline_info()
        logger.info(f"✓ Data pipeline ready")
        logger.info(f"  - Data directory: {pipeline_info['data_directory']}")
        logger.info(f"  - Available datasets: {len(pipeline_info['available_datasets'])}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Setup failed: {str(e)}")
        return False

async def demo_synthetic_data():
    """Demo synthetic data generation"""
    print_section("Generating Synthetic Data")
    
    try:
        async with AsyncSessionLocal() as db:
            # Generate small amount of synthetic data
            logger.info("Generating 50 synthetic users...")
            results = await data_pipeline.generate_synthetic_data(db, num_users=50)
            
            if results:
                logger.info(f"✓ Generated {results['users']} users")
                logger.info(f"✓ Generated {results['bets']} bets")
                logger.info(f"✓ Generated {results['interactions']} interactions")
                
                # Show some sample data
                await show_sample_data(db)
                return True
            else:
                logger.error("✗ Synthetic data generation failed")
                return False
                
    except Exception as e:
        logger.error(f"✗ Synthetic data demo failed: {str(e)}")
        return False

async def show_sample_data(db):
    """Show sample data from the database"""
    print_section("Sample Data Overview")
    
    try:
        # Count records
        result = await db.execute("SELECT COUNT(*) as count FROM users")
        user_count = result.fetchone().count
        
        result = await db.execute("SELECT COUNT(*) as count FROM bets")
        bet_count = result.fetchone().count
        
        result = await db.execute("SELECT COUNT(*) as count FROM interactions")
        interaction_count = result.fetchone().count
        
        logger.info(f"📊 Database Summary:")
        logger.info(f"  - Users: {user_count}")
        logger.info(f"  - Bets: {bet_count}")
        logger.info(f"  - Interactions: {interaction_count}")
        
        # Show sample user
        result = await db.execute("""
            SELECT username, favorite_sport, total_bets, win_rate, user_tier
            FROM users 
            LIMIT 1
        """)
        user = result.fetchone()
        if user:
            logger.info(f"👤 Sample User:")
            logger.info(f"  - Username: {user.username}")
            logger.info(f"  - Favorite Sport: {user.favorite_sport}")
            logger.info(f"  - Total Bets: {user.total_bets}")
            logger.info(f"  - Win Rate: {user.win_rate:.1%}")
            logger.info(f"  - Tier: {user.user_tier}")
        
        # Show sample bet
        result = await db.execute("""
            SELECT bet_type, sport, team_a, team_b, stake, result, profit_loss
            FROM bets 
            LIMIT 1
        """)
        bet = result.fetchone()
        if bet:
            logger.info(f"🎯 Sample Bet:")
            logger.info(f"  - Type: {bet.bet_type}")
            logger.info(f"  - Sport: {bet.sport}")
            logger.info(f"  - Teams: {bet.team_a} vs {bet.team_b}")
            logger.info(f"  - Stake: ${bet.stake:.2f}")
            logger.info(f"  - Result: {bet.result}")
            logger.info(f"  - P&L: ${bet.profit_loss:.2f}")
        
        # Show sample interaction
        result = await db.execute("""
            SELECT interaction_type, sentiment_label, sentiment_score, content
            FROM interactions 
            LIMIT 1
        """)
        interaction = result.fetchone()
        if interaction:
            logger.info(f"💬 Sample Interaction:")
            logger.info(f"  - Type: {interaction.interaction_type}")
            logger.info(f"  - Sentiment: {interaction.sentiment_label}")
            logger.info(f"  - Score: {interaction.sentiment_score:.2f}")
            logger.info(f"  - Content: {interaction.content[:100]}...")
            
    except Exception as e:
        logger.error(f"✗ Error showing sample data: {str(e)}")

async def demo_analytics():
    """Demo basic analytics capabilities"""
    print_section("Basic Analytics Demo")
    
    try:
        async with AsyncSessionLocal() as db:
            # User demographics
            result = await db.execute("""
                SELECT 
                    favorite_sport,
                    COUNT(*) as user_count,
                    AVG(total_bets) as avg_bets,
                    AVG(win_rate) as avg_win_rate
                FROM users 
                GROUP BY favorite_sport
                ORDER BY user_count DESC
            """)
            
            sports_data = result.fetchall()
            logger.info("🏈 Sports Preferences:")
            for sport in sports_data:
                logger.info(f"  - {sport.favorite_sport}: {sport.user_count} users, "
                          f"avg {sport.avg_bets:.1f} bets, {sport.avg_win_rate:.1%} win rate")
            
            # Betting performance
            result = await db.execute("""
                SELECT 
                    bet_type,
                    COUNT(*) as bet_count,
                    AVG(stake) as avg_stake,
                    SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losses
                FROM bets 
                GROUP BY bet_type
                ORDER BY bet_count DESC
            """)
            
            bet_data = result.fetchall()
            logger.info("\n🎲 Betting Performance by Type:")
            for bet_type in bet_data:
                total = bet_type.wins + bet_type.losses
                win_rate = bet_type.wins / total if total > 0 else 0
                logger.info(f"  - {bet_type.bet_type}: {bet_type.bet_count} bets, "
                          f"avg stake ${bet_type.avg_stake:.2f}, {win_rate:.1%} win rate")
            
            # Sentiment analysis
            result = await db.execute("""
                SELECT 
                    sentiment_label,
                    COUNT(*) as count,
                    AVG(sentiment_score) as avg_score
                FROM interactions 
                GROUP BY sentiment_label
                ORDER BY count DESC
            """)
            
            sentiment_data = result.fetchall()
            logger.info("\n😊 Sentiment Analysis:")
            for sentiment in sentiment_data:
                logger.info(f"  - {sentiment.sentiment_label}: {sentiment.count} interactions, "
                          f"avg score {sentiment.avg_score:.2f}")
            
            return True
            
    except Exception as e:
        logger.error(f"✗ Analytics demo failed: {str(e)}")
        return False

async def demo_cleanup():
    """Demo data cleanup"""
    print_section("Data Cleanup Demo")
    
    try:
        async with AsyncSessionLocal() as db:
            # Count records before cleanup
            result = await db.execute("SELECT COUNT(*) as count FROM users")
            users_before = result.fetchone().count
            
            result = await db.execute("SELECT COUNT(*) as count FROM bets")
            bets_before = result.fetchone().count
            
            logger.info(f"📊 Records before cleanup: {users_before} users, {bets_before} bets")
            
            # Perform cleanup
            logger.info("🧹 Cleaning up demo data...")
            success = await data_pipeline.cleanup_data(db)
            
            if success:
                # Verify cleanup
                result = await db.execute("SELECT COUNT(*) as count FROM users")
                users_after = result.fetchone().count
                
                result = await db.execute("SELECT COUNT(*) as count FROM bets")
                bets_after = result.fetchone().count
                
                if users_after == 0 and bets_after == 0:
                    logger.info("✓ Data cleanup successful - all demo records removed")
                    return True
                else:
                    logger.error(f"✗ Data cleanup incomplete: {users_after} users, {bets_after} bets remaining")
                    return False
            else:
                logger.error("✗ Data cleanup operation failed")
                return False
                
    except Exception as e:
        logger.error(f"✗ Cleanup demo failed: {str(e)}")
        return False

async def run_demo():
    """Run the complete demo"""
    try:
        # Setup
        if not await demo_setup():
            return False
        
        # Generate data
        if not await demo_synthetic_data():
            return False
        
        # Show analytics
        if not await demo_analytics():
            return False
        
        # Cleanup
        if not await demo_cleanup():
            return False
        
        print_header("🎉 DEMO COMPLETED SUCCESSFULLY!")
        logger.info("The data pipeline demo has completed successfully!")
        logger.info("Key features demonstrated:")
        logger.info("  ✓ Synthetic data generation")
        logger.info("  ✓ Database operations")
        logger.info("  ✓ Basic analytics")
        logger.info("  ✓ Data cleanup")
        logger.info("\nNext steps:")
        logger.info("  - Try the full data pipeline with real datasets")
        logger.info("  - Explore the API endpoints")
        logger.info("  - Check out the frontend dashboard")
        
        return True
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        return False

async def main():
    """Main demo execution"""
    try:
        success = await run_demo()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during demo: {str(e)}")
        sys.exit(1)
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
