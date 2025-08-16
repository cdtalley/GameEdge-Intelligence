"""
Data Pipeline for GameEdge Intelligence Platform

Handles downloading, transformation, and loading of primary datasets:
- Sentiment140 (Twitter sentiment analysis)
- Online Retail II UCI (customer behavior)
- Beat The Bookie Football Dataset (sports betting odds)
"""

import asyncio
import logging
import os
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import aiohttp
import aiofiles
from tqdm import tqdm

from ..models import User, Bet, Interaction, Segment, UserSegment
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class DataPipeline:
    """Main data pipeline for downloading and transforming datasets"""
    
    def __init__(self):
        self.data_dir = Path(settings.DATA_DIR)
        self.data_dir.mkdir(exist_ok=True)
        
        # Dataset URLs and metadata
        self.datasets = {
            "sentiment140": {
                "url": "https://www.kaggle.com/datasets/kazanova/sentiment140",
                "filename": "sentiment140.csv",
                "size_mb": 80,
                "description": "Twitter sentiment analysis dataset"
            },
            "online_retail": {
                "url": "https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci",
                "filename": "online_retail_ii.csv",
                "size_mb": 45,
                "description": "Online retail customer behavior dataset"
            },
            "football_odds": {
                "url": "https://www.kaggle.com/datasets/austro/beat-the-bookie-worldwide-football-dataset",
                "filename": "football_odds.csv",
                "size_mb": 120,
                "description": "Football betting odds and results dataset"
            }
        }
        
        # Sports mapping for transformation
        self.sports_mapping = {
            "football": ["soccer", "football", "futbol"],
            "basketball": ["basketball", "basket", "hoops"],
            "baseball": ["baseball", "base", "ball"],
            "tennis": ["tennis", "tenis"],
            "hockey": ["hockey", "ice hockey", "hock"],
            "golf": ["golf", "golfing"],
            "racing": ["racing", "race", "f1", "nascar", "motorsport"],
            "esports": ["esports", "gaming", "csgo", "lol", "dota"]
        }
        
        # Bet types for transformation
        self.bet_types = [
            "moneyline", "spread", "over_under", "parlay", "prop_bet",
            "futures", "live_betting", "teaser", "if_bet", "reverse_bet"
        ]
    
    async def download_dataset(self, dataset_name: str, kaggle_token: str) -> bool:
        """Download dataset from Kaggle using API token"""
        if dataset_name not in self.datasets:
            logger.error(f"Unknown dataset: {dataset_name}")
            return False
        
        dataset_info = self.datasets[dataset_name]
        output_path = self.data_dir / dataset_info["filename"]
        
        if output_path.exists():
            logger.info(f"Dataset {dataset_name} already exists at {output_path}")
            return True
        
        try:
            # Set Kaggle credentials
            kaggle_dir = Path.home() / ".kaggle"
            kaggle_dir.mkdir(exist_ok=True)
            
            kaggle_config = kaggle_dir / "kaggle.json"
            if not kaggle_config.exists():
                # Parse Kaggle token (username:key format)
                if ":" in kaggle_token:
                    username, key = kaggle_token.split(":", 1)
                    config_content = f'{{"username": "{username}", "key": "{key}"}}'
                    async with aiofiles.open(kaggle_config, 'w') as f:
                        await f.write(config_content)
                else:
                    logger.error("Invalid Kaggle token format. Expected 'username:key'")
                    return False
            
            # Download using Kaggle CLI
            import subprocess
            cmd = f"kaggle datasets download -d {dataset_name} -p {self.data_dir}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully downloaded {dataset_name}")
                return True
            else:
                logger.error(f"Failed to download {dataset_name}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading {dataset_name}: {str(e)}")
            return False
    
    async def transform_sentiment140(self, db: AsyncSession) -> int:
        """Transform Sentiment140 dataset into betting interactions"""
        file_path = self.data_dir / "sentiment140.csv"
        if not file_path.exists():
            logger.error("Sentiment140 dataset not found")
            return 0
        
        try:
            # Read dataset
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} sentiment records")
            
            # Transform to betting interactions
            interactions = []
            for _, row in tqdm(df.iterrows(), total=len(df), desc="Transforming sentiment data"):
                # Map sentiment to betting context
                sentiment_label = "positive" if row["target"] == 0 else "negative"
                confidence = np.random.uniform(0.7, 0.95)
                
                # Generate betting-related text
                betting_text = self._generate_betting_text(row["text"], sentiment_label)
                
                interaction = Interaction(
                    user_id=np.random.randint(1, 1000),  # Random user assignment
                    interaction_type="review",
                    content=betting_text,
                    sentiment_label=sentiment_label,
                    sentiment_score=confidence,
                    sentiment_confidence=confidence,
                    aspect_sentiment={"overall": sentiment_label},
                    created_at=pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(1, 365))
                )
                interactions.append(interaction)
            
            # Batch insert
            db.add_all(interactions)
            await db.commit()
            
            logger.info(f"Transformed and inserted {len(interactions)} betting interactions")
            return len(interactions)
            
        except Exception as e:
            logger.error(f"Error transforming Sentiment140: {str(e)}")
            await db.rollback()
            return 0
    
    async def transform_online_retail(self, db: AsyncSession) -> int:
        """Transform Online Retail dataset into betting customers and transactions"""
        file_path = self.data_dir / "online_retail_ii.csv"
        if not file_path.exists():
            logger.error("Online Retail dataset not found")
            return 0
        
        try:
            # Read dataset
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} retail records")
            
            # Transform customers
            customers = df.groupby("Customer ID").agg({
                "InvoiceDate": ["min", "max", "count"],
                "Quantity": "sum",
                "Price": lambda x: (x * df.loc[x.index, "Quantity"]).sum()
            }).reset_index()
            
            customers.columns = ["customer_id", "first_purchase", "last_purchase", "total_purchases", "total_quantity", "total_spent"]
            
            # Create users
            users = []
            for _, customer in tqdm(customers.iterrows(), total=len(customers), desc="Creating betting users"):
                user = User(
                    id=customer["customer_id"],
                    username=f"user_{customer['customer_id']}",
                    email=f"user_{customer['customer_id']}@example.com",
                    first_name=f"User{customer['customer_id']}",
                    last_name="",
                    date_of_birth=pd.Timestamp("1980-01-01") + pd.Timedelta(days=np.random.randint(0, 10000)),
                    favorite_sport=np.random.choice(list(self.sports_mapping.keys())),
                    risk_tolerance=np.random.choice(["low", "medium", "high"]),
                    total_deposits=customer["total_spent"] * np.random.uniform(1.5, 3.0),
                    lifetime_value=customer["total_spent"] * np.random.uniform(2.0, 4.0),
                    total_bets=customer["total_purchases"],
                    win_rate=np.random.uniform(0.4, 0.6),
                    rfm_recency=365 - (pd.Timestamp.now() - customer["last_purchase"]).days,
                    rfm_frequency=customer["total_purchases"],
                    rfm_monetary=customer["total_spent"],
                    user_tier=np.random.choice(["bronze", "silver", "gold", "platinum"]),
                    status="active",
                    created_at=customer["first_purchase"],
                    updated_at=customer["last_purchase"]
                )
                users.append(user)
            
            # Create bets from retail transactions
            bets = []
            for _, row in tqdm(df.iterrows(), total=len(df), desc="Creating betting transactions"):
                bet = Bet(
                    user_id=row["Customer ID"],
                    bet_type=np.random.choice(self.bet_types),
                    sport=np.random.choice(list(self.sports_mapping.keys())),
                    team_a=f"Team A {row['StockCode']}",
                    team_b=f"Team B {row['StockCode']}",
                    odds=np.random.uniform(1.5, 5.0),
                    stake=row["Quantity"] * row["Price"],
                    potential_payout=row["Quantity"] * row["Price"] * np.random.uniform(1.2, 3.0),
                    game_date=row["InvoiceDate"],
                    bet_status="settled",
                    result="win" if np.random.random() > 0.5 else "loss",
                    profit_loss=row["Quantity"] * row["Price"] * np.random.uniform(-0.8, 1.5),
                    created_at=row["InvoiceDate"]
                )
                bets.append(bet)
            
            # Batch insert
            db.add_all(users)
            db.add_all(bets)
            await db.commit()
            
            logger.info(f"Transformed and inserted {len(users)} users and {len(bets)} bets")
            return len(users) + len(bets)
            
        except Exception as e:
            logger.error(f"Error transforming Online Retail: {str(e)}")
            await db.rollback()
            return 0
    
    async def transform_football_odds(self, db: AsyncSession) -> int:
        """Transform Football Odds dataset into betting data"""
        file_path = self.data_dir / "football_odds.csv"
        if not file_path.exists():
            logger.error("Football Odds dataset not found")
            return 0
        
        try:
            # Read dataset
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} football odds records")
            
            # Transform odds data into bets
            bets = []
            for _, row in tqdm(df.iterrows(), total=len(df), desc="Creating football bets"):
                # Skip if missing required data
                if pd.isna(row.get("HomeTeam")) or pd.isna(row.get("AwayTeam")):
                    continue
                
                bet = Bet(
                    user_id=np.random.randint(1, 1000),  # Random user assignment
                    bet_type="moneyline",
                    sport="football",
                    team_a=row["HomeTeam"],
                    team_b=row["AwayTeam"],
                    odds=row.get("AvgH", 2.0),  # Home team odds
                    stake=np.random.uniform(10, 1000),
                    potential_payout=np.random.uniform(10, 1000) * row.get("AvgH", 2.0),
                    game_date=pd.to_datetime(row.get("Date", pd.Timestamp.now())),
                    bet_status="settled",
                    result="win" if np.random.random() > 0.6 else "loss",  # Slight bias towards wins
                    profit_loss=np.random.uniform(-100, 200),
                    created_at=pd.to_datetime(row.get("Date", pd.Timestamp.now()))
                )
                bets.append(bet)
            
            # Batch insert
            db.add_all(bets)
            await db.commit()
            
            logger.info(f"Transformed and inserted {len(bets)} football bets")
            return len(bets)
            
        except Exception as e:
            logger.error(f"Error transforming Football Odds: {str(e)}")
            await db.rollback()
            return 0
    
    def _generate_betting_text(self, original_text: str, sentiment: str) -> str:
        """Generate betting-related text from original sentiment text"""
        betting_templates = {
            "positive": [
                "Great betting experience! The odds were fair and the payout was excellent.",
                "Amazing win today! The sportsbook handled everything perfectly.",
                "Fantastic betting platform with great customer service.",
                "Love the live betting features and real-time updates.",
                "Best sportsbook I've ever used - highly recommend!"
            ],
            "negative": [
                "Terrible experience with this sportsbook. Odds were terrible.",
                "Lost money due to poor customer service and slow payouts.",
                "The betting interface is confusing and frustrating to use.",
                "Avoid this platform - they don't honor their promises.",
                "Worst betting experience ever. Don't waste your time."
            ]
        }
        
        # Use template based on sentiment
        templates = betting_templates.get(sentiment, betting_templates["positive"])
        return np.random.choice(templates)
    
    async def run_full_pipeline(self, db: AsyncSession, kaggle_token: str) -> Dict[str, int]:
        """Run the complete data pipeline"""
        results = {}
        
        logger.info("Starting full data pipeline...")
        
        # Download datasets
        for dataset_name in self.datasets.keys():
            logger.info(f"Downloading {dataset_name}...")
            success = await self.download_dataset(dataset_name, kaggle_token)
            if success:
                logger.info(f"Successfully downloaded {dataset_name}")
            else:
                logger.warning(f"Failed to download {dataset_name}")
        
        # Transform and load data
        logger.info("Transforming and loading data...")
        
        # Sentiment140 -> Interactions
        results["interactions"] = await self.transform_sentiment140(db)
        
        # Online Retail -> Users + Bets
        results["users_bets"] = await self.transform_online_retail(db)
        
        # Football Odds -> Additional Bets
        results["football_bets"] = await self.transform_football_odds(db)
        
        logger.info("Data pipeline completed successfully!")
        return results
    
    async def generate_synthetic_data(self, db: AsyncSession, num_users: int = 1000) -> Dict[str, int]:
        """Generate synthetic data for testing and development"""
        logger.info(f"Generating synthetic data for {num_users} users...")
        
        try:
            # Generate users
            users = []
            for i in range(num_users):
                user = User(
                    username=f"synthetic_user_{i}",
                    email=f"user{i}@example.com",
                    first_name=f"User{i}",
                    last_name="Synthetic",
                    date_of_birth=pd.Timestamp("1980-01-01") + pd.Timedelta(days=np.random.randint(0, 10000)),
                    favorite_sport=np.random.choice(list(self.sports_mapping.keys())),
                    risk_tolerance=np.random.choice(["low", "medium", "high"]),
                    total_deposits=np.random.uniform(100, 10000),
                    lifetime_value=np.random.uniform(200, 20000),
                    total_bets=np.random.randint(10, 500),
                    win_rate=np.random.uniform(0.3, 0.7),
                    rfm_recency=np.random.randint(1, 365),
                    rfm_frequency=np.random.randint(1, 100),
                    rfm_monetary=np.random.uniform(100, 10000),
                    user_tier=np.random.choice(["bronze", "silver", "gold", "platinum"]),
                    status="active"
                )
                users.append(user)
            
            # Generate bets
            bets = []
            for user in users:
                num_bets = np.random.randint(5, 50)
                for _ in range(num_bets):
                    bet = Bet(
                        user_id=user.id,
                        bet_type=np.random.choice(self.bet_types),
                        sport=np.random.choice(list(self.sports_mapping.keys())),
                        team_a=f"Team A {np.random.randint(1, 100)}",
                        team_b=f"Team B {np.random.randint(1, 100)}",
                        odds=np.random.uniform(1.2, 10.0),
                        stake=np.random.uniform(10, 1000),
                        potential_payout=np.random.uniform(10, 1000) * np.random.uniform(1.2, 3.0),
                        game_date=pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(1, 365)),
                        bet_status="settled",
                        result="win" if np.random.random() > 0.5 else "loss",
                        profit_loss=np.random.uniform(-500, 1000)
                    )
                    bets.append(bet)
            
            # Generate interactions
            interactions = []
            for user in users:
                num_interactions = np.random.randint(1, 10)
                for _ in range(num_interactions):
                    sentiment = np.random.choice(["positive", "negative", "neutral"])
                    interaction = Interaction(
                        user_id=user.id,
                        interaction_type="review",
                        content=f"Synthetic review for user {user.id}",
                        sentiment_label=sentiment,
                        sentiment_score=np.random.uniform(0.1, 0.9),
                        sentiment_confidence=np.random.uniform(0.7, 0.95),
                        aspect_sentiment={"overall": sentiment}
                    )
                    interactions.append(interaction)
            
            # Batch insert
            db.add_all(users)
            db.add_all(bets)
            db.add_all(interactions)
            await db.commit()
            
            logger.info(f"Generated {len(users)} users, {len(bets)} bets, {len(interactions)} interactions")
            return {
                "users": len(users),
                "bets": len(bets),
                "interactions": len(interactions)
            }
            
        except Exception as e:
            logger.error(f"Error generating synthetic data: {str(e)}")
            await db.rollback()
            return {}
    
    async def cleanup_data(self, db: AsyncSession) -> bool:
        """Clean up all data from the database"""
        try:
            logger.info("Cleaning up all data...")
            
            # Delete in reverse dependency order
            await db.execute(text("DELETE FROM user_segments"))
            await db.execute(text("DELETE FROM interactions"))
            await db.execute(text("DELETE FROM bets"))
            await db.execute(text("DELETE FROM users"))
            await db.execute(text("DELETE FROM segments"))
            
            await db.commit()
            logger.info("Data cleanup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during data cleanup: {str(e)}")
            await db.rollback()
            return False

# Global instance
data_pipeline = DataPipeline()
