import logging
from typing import Dict, List, Tuple, Optional, Any, Union
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import joblib
import os
from datetime import datetime, timedelta

from ..core.config import settings
from ..models import User, Bet, Interaction, Segment, UserSegment

logger = logging.getLogger(__name__)


class CustomerSegmentationEngine:
    """
    Advanced customer segmentation engine with RFM analysis, clustering algorithms,
    and churn prediction for sports betting customers.
    """
    
    def __init__(self):
        self.rfm_scaler = StandardScaler()
        self.clustering_scaler = StandardScaler()
        self.churn_model = None
        self.segments = {}
        self.is_initialized = False
        
        # RFM scoring parameters
        self.rfm_weights = {
            'recency': 0.3,
            'frequency': 0.3,
            'monetary': 0.4
        }
        
        # Clustering parameters
        self.n_clusters = 5
        self.min_cluster_size = 10
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize segmentation models"""
        try:
            # Initialize churn prediction model
            self._setup_churn_model()
            
            self.is_initialized = True
            logger.info("Customer segmentation engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize segmentation engine: {e}")
            self.is_initialized = False
    
    def _setup_churn_model(self):
        """Setup churn prediction model"""
        try:
            # Random Forest for churn prediction
            self.churn_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            logger.info("Churn prediction model initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup churn model: {e}")
            self.churn_model = None
    
    def calculate_rfm_scores(self, users_data: pd.DataFrame, reference_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Calculate RFM scores for users based on their betting behavior.
        
        Args:
            users_data: DataFrame with user transaction data
            reference_date: Reference date for calculations (defaults to current date)
            
        Returns:
            DataFrame with RFM scores
        """
        if reference_date is None:
            reference_date = datetime.utcnow()
        
        try:
            # Calculate Recency (days since last activity)
            users_data['recency_days'] = (reference_date - pd.to_datetime(users_data['last_activity'])).dt.days
            
            # Calculate Frequency (number of transactions)
            users_data['frequency'] = users_data['total_bets']
            
            # Calculate Monetary (total value)
            users_data['monetary'] = users_data['lifetime_value']
            
            # Calculate RFM scores (1-5 scale)
            users_data['recency_score'] = self._score_recency(users_data['recency_days'])
            users_data['frequency_score'] = self._score_frequency(users_data['frequency'])
            users_data['monetary_score'] = self._score_monetary(users_data['monetary'])
            
            # Calculate composite RFM score
            users_data['rfm_score'] = (
                users_data['recency_score'] * self.rfm_weights['recency'] +
                users_data['frequency_score'] * self.rfm_weights['frequency'] +
                users_data['monetary_score'] * self.rfm_weights['monetary']
            )
            
            # Assign RFM segments
            users_data['rfm_segment'] = self._assign_rfm_segment(users_data['rfm_score'])
            
            return users_data
            
        except Exception as e:
            logger.error(f"RFM calculation failed: {e}")
            return pd.DataFrame()
    
    def _score_recency(self, recency_days: pd.Series) -> pd.Series:
        """Score recency on 1-5 scale"""
        # Lower days = higher score
        bins = [0, 7, 30, 90, 180, float('inf')]
        labels = [5, 4, 3, 2, 1]
        return pd.cut(recency_days, bins=bins, labels=labels, include_lowest=True).astype(int)
    
    def _score_frequency(self, frequency: pd.Series) -> pd.Series:
        """Score frequency on 1-5 scale"""
        # Higher frequency = higher score
        bins = [0, 1, 5, 15, 50, float('inf')]
        labels = [1, 2, 3, 4, 5]
        return pd.cut(frequency, bins=bins, labels=labels, include_lowest=True).astype(int)
    
    def _score_monetary(self, monetary: pd.Series) -> pd.Series:
        """Score monetary on 1-5 scale"""
        # Higher monetary = higher score
        bins = [0, 100, 500, 2000, 10000, float('inf')]
        labels = [1, 2, 3, 4, 5]
        return pd.cut(monetary, bins=bins, labels=labels, include_lowest=True).astype(int)
    
    def _assign_rfm_segment(self, rfm_score: pd.Series) -> pd.Series:
        """Assign RFM segments based on composite score"""
        bins = [0, 2, 3, 4, float('inf')]
        labels = ['At Risk', 'Low Value', 'Medium Value', 'High Value']
        return pd.cut(rfm_score, bins=bins, labels=labels, include_lowest=True)
    
    def perform_clustering(self, users_data: pd.DataFrame, method: str = 'kmeans') -> pd.DataFrame:
        """
        Perform customer clustering using specified method.
        
        Args:
            users_data: DataFrame with user features
            method: Clustering method ('kmeans' or 'dbscan')
            
        Returns:
            DataFrame with cluster assignments
        """
        try:
            # Prepare features for clustering
            feature_columns = [
                'recency_score', 'frequency_score', 'monetary_score',
                'win_rate', 'average_bet_size', 'total_bets'
            ]
            
            # Filter out users with missing data
            clustering_data = users_data[feature_columns].dropna()
            
            if clustering_data.empty:
                logger.warning("No data available for clustering")
                return users_data
            
            # Scale features
            scaled_features = self.clustering_scaler.fit_transform(clustering_data)
            
            if method == 'kmeans':
                clusters = self._kmeans_clustering(scaled_features)
            elif method == 'dbscan':
                clusters = self._dbscan_clustering(scaled_features)
            else:
                logger.error(f"Unknown clustering method: {method}")
                return users_data
            
            # Assign clusters back to original data
            users_data.loc[clustering_data.index, 'cluster'] = clusters
            users_data['cluster'] = users_data['cluster'].fillna(-1).astype(int)
            
            return users_data
            
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            return users_data
    
    def _kmeans_clustering(self, features: np.ndarray) -> np.ndarray:
        """Perform K-means clustering"""
        # Determine optimal number of clusters
        silhouette_scores = []
        k_range = range(2, min(10, len(features) // 10))
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(features)
            silhouette_avg = silhouette_score(features, cluster_labels)
            silhouette_scores.append(silhouette_avg)
        
        # Use optimal k
        optimal_k = k_range[np.argmax(silhouette_scores)]
        
        # Perform final clustering
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        return kmeans.fit_predict(features)
    
    def _dbscan_clustering(self, features: np.ndarray) -> np.ndarray:
        """Perform DBSCAN clustering"""
        # Determine optimal epsilon using nearest neighbors
        from sklearn.neighbors import NearestNeighbors
        
        nn = NearestNeighbors(n_neighbors=min(5, len(features) - 1))
        nn.fit(features)
        distances, _ = nn.kneighbors(features)
        
        # Use 95th percentile of distances as epsilon
        epsilon = np.percentile(distances[:, -1], 95)
        
        dbscan = DBSCAN(eps=epsilon, min_samples=self.min_cluster_size)
        return dbscan.fit_predict(features)
    
    def predict_churn(self, users_data: pd.DataFrame) -> pd.DataFrame:
        """
        Predict churn probability for users.
        
        Args:
            users_data: DataFrame with user features
            
        Returns:
            DataFrame with churn predictions
        """
        if self.churn_model is None:
            logger.warning("Churn model not available")
            return users_data
        
        try:
            # Prepare features for churn prediction
            feature_columns = [
                'recency_days', 'frequency', 'monetary', 'win_rate',
                'average_bet_size', 'total_bets', 'rfm_score'
            ]
            
            # Filter out users with missing data
            churn_data = users_data[feature_columns].dropna()
            
            if churn_data.empty:
                logger.warning("No data available for churn prediction")
                return users_data
            
            # Create churn labels (simplified - users inactive for >30 days)
            churn_labels = (churn_data['recency_days'] > 30).astype(int)
            
            # Train churn model if we have enough data
            if len(churn_data) > 50:
                X_train, X_test, y_train, y_test = train_test_split(
                    churn_data, churn_labels, test_size=0.2, random_state=42
                )
                
                self.churn_model.fit(X_train, y_train)
                
                # Calculate feature importance
                feature_importance = dict(zip(feature_columns, self.churn_model.feature_importances_))
                logger.info(f"Churn model feature importance: {feature_importance}")
            
            # Predict churn probability
            churn_proba = self.churn_model.predict_proba(churn_data)[:, 1]
            
            # Assign churn predictions back to original data
            users_data.loc[churn_data.index, 'churn_probability'] = churn_proba
            
            # Assign churn risk levels
            users_data['churn_risk_level'] = users_data['churn_probability'].apply(
                lambda x: self._assign_churn_risk(x) if pd.notna(x) else 'unknown'
            )
            
            return users_data
            
        except Exception as e:
            logger.error(f"Churn prediction failed: {e}")
            return users_data
    
    def _assign_churn_risk(self, probability: float) -> str:
        """Assign churn risk level based on probability"""
        if probability < 0.3:
            return 'low'
        elif probability < 0.7:
            return 'medium'
        else:
            return 'high'
    
    def create_segments(self, users_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Create customer segments based on analysis results.
        
        Args:
            users_data: DataFrame with user analysis results
            
        Returns:
            Dictionary with segment information
        """
        try:
            segments = {}
            
            # RFM-based segments
            rfm_segments = users_data['rfm_segment'].value_counts()
            for segment_name, count in rfm_segments.items():
                segment_data = users_data[users_data['rfm_segment'] == segment_name]
                segments[f"RFM_{segment_name}"] = {
                    'type': 'rfm',
                    'user_count': int(count),
                    'avg_lifetime_value': float(segment_data['lifetime_value'].mean()),
                    'avg_churn_risk': float(segment_data['churn_probability'].mean()),
                    'criteria': {'rfm_segment': segment_name}
                }
            
            # Cluster-based segments
            if 'cluster' in users_data.columns:
                cluster_segments = users_data['cluster'].value_counts()
                for cluster_id, count in cluster_segments.items():
                    if cluster_id != -1:  # Skip noise points
                        cluster_data = users_data[users_data['cluster'] == cluster_id]
                        segments[f"Cluster_{cluster_id}"] = {
                            'type': 'clustering',
                            'user_count': int(count),
                            'avg_lifetime_value': float(cluster_data['lifetime_value'].mean()),
                            'avg_churn_risk': float(cluster_data['churn_probability'].mean()),
                            'criteria': {'cluster_id': int(cluster_id)}
                        }
            
            # High-value customer segment
            high_value_threshold = users_data['lifetime_value'].quantile(0.8)
            high_value_users = users_data[users_data['lifetime_value'] >= high_value_threshold]
            segments['High_Value_Customers'] = {
                'type': 'behavioral',
                'user_count': len(high_value_users),
                'avg_lifetime_value': float(high_value_users['lifetime_value'].mean()),
                'avg_churn_risk': float(high_value_users['churn_probability'].mean()),
                'criteria': {'lifetime_value': f">={high_value_threshold}"}
            }
            
            # At-risk customers
            at_risk_users = users_data[users_data['churn_risk_level'] == 'high']
            segments['At_Risk_Customers'] = {
                'type': 'behavioral',
                'user_count': len(at_risk_users),
                'avg_lifetime_value': float(at_risk_users['lifetime_value'].mean()),
                'avg_churn_risk': float(at_risk_users['churn_probability'].mean()),
                'criteria': {'churn_risk_level': 'high'}
            }
            
            self.segments = segments
            return segments
            
        except Exception as e:
            logger.error(f"Segment creation failed: {e}")
            return {}
    
    def get_segment_recommendations(self, user_id: int, users_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Get personalized recommendations for a specific user.
        
        Args:
            user_id: User ID to get recommendations for
            users_data: DataFrame with user analysis results
            
        Returns:
            Dictionary with personalized recommendations
        """
        try:
            user_data = users_data[users_data['id'] == user_id]
            
            if user_data.empty:
                return {"error": "User not found"}
            
            user_data = user_data.iloc[0]
            recommendations = {
                'user_id': user_id,
                'current_segment': user_data.get('rfm_segment', 'Unknown'),
                'churn_risk': user_data.get('churn_risk_level', 'unknown'),
                'recommendations': []
            }
            
            # Generate recommendations based on user profile
            if user_data.get('churn_risk_level') == 'high':
                recommendations['recommendations'].append({
                    'type': 'retention',
                    'priority': 'high',
                    'message': 'Consider offering personalized promotions to re-engage this customer'
                })
            
            if user_data.get('rfm_segment') == 'At Risk':
                recommendations['recommendations'].append({
                    'type': 'engagement',
                    'priority': 'high',
                    'message': 'Send targeted communication to increase engagement'
                })
            
            if user_data.get('lifetime_value', 0) > 1000:
                recommendations['recommendations'].append({
                    'type': 'upsell',
                    'priority': 'medium',
                    'message': 'Offer VIP services and exclusive betting opportunities'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return {"error": str(e)}
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get status of the segmentation engine"""
        return {
            'is_initialized': self.is_initialized,
            'churn_model_available': self.churn_model is not None,
            'segments_created': len(self.segments),
            'rfm_weights': self.rfm_weights,
            'clustering_params': {
                'n_clusters': self.n_clusters,
                'min_cluster_size': self.min_cluster_size
            }
        }


# Global instance
segmentation_engine = CustomerSegmentationEngine()
