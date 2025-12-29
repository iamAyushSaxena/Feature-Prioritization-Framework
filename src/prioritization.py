"""
RICE Prioritization Framework Implementation
Calculates Reach, Impact, Confidence, and Effort scores for features
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from config import *


class RICEFramework:
    """
    RICE Scoring Framework for Feature Prioritization
    RICE Score = (Reach × Impact × Confidence) / Effort
    """
    
    def __init__(self, features_data: pd.DataFrame):
        """
        Initialize RICE Framework with feature data
        
        Args:
            features_data: DataFrame with columns [feature_name, category, reach, 
                          impact, confidence, effort, description]
        """
        self.features_data = features_data.copy()
        self.rice_scores = None
        
    def calculate_reach(self, reach_percentage: float) -> float:
        """
        Calculate reach score based on percentage of users affected
        
        Args:
            reach_percentage: Percentage of MAU affected (0-100)
            
        Returns:
            Absolute number of users reached per month
        """
        return (reach_percentage / 100) * MONTHLY_ACTIVE_USERS
    
    def calculate_impact_score(self, impact_level: str) -> float:
        """
        Convert qualitative impact to quantitative score
        
        Args:
            impact_level: One of ['Massive', 'High', 'Medium', 'Low', 'Minimal']
            
        Returns:
            Impact score (0.25 to 3)
        """
        return IMPACT_SCALE.get(impact_level, 1)
    
    def calculate_confidence_score(self, confidence_level: str) -> float:
        """
        Convert confidence level to percentage
        
        Args:
            confidence_level: One of ['High', 'Medium', 'Low']
            
        Returns:
            Confidence as decimal (0.5 to 1.0)
        """
        return CONFIDENCE_SCALE.get(confidence_level, 80) / 100
    
    def calculate_rice_score(self, reach: float, impact: float, 
                            confidence: float, effort: float) -> float:
        """
        Calculate final RICE score
        
        Args:
            reach: Number of users reached
            impact: Impact score (0.25-3)
            confidence: Confidence percentage (0-100)
            effort: Effort in person-months
            
        Returns:
            RICE score
        """
        if effort == 0:
            return 0
        
        return (reach * impact * confidence) / effort
    
    def prioritize_features(self) -> pd.DataFrame:
        """
        Calculate RICE scores for all features and rank them
        
        Returns:
            DataFrame with RICE scores and rankings
        """
        # Calculate reach in absolute numbers
        self.features_data['reach_users'] = self.features_data['reach_percentage'].apply(
            self.calculate_reach
        )
        
        # Convert impact to numerical scores
        self.features_data['impact_score'] = self.features_data['impact_level'].apply(
            self.calculate_impact_score
        )
        
        # Convert confidence to decimal
        self.features_data['confidence_score'] = self.features_data['confidence_level'].apply(
            self.calculate_confidence_score
        )
        
        # Calculate RICE score
        self.features_data['rice_score'] = self.features_data.apply(
            lambda row: self.calculate_rice_score(
                row['reach_users'],
                row['impact_score'],
                row['confidence_score'],
                row['effort_months']
            ),
            axis=1
        )
        
        # Rank features
        self.features_data['rank'] = self.features_data['rice_score'].rank(
            ascending=False, method='dense'
        ).astype(int)
        
        # Sort by rank
        self.rice_scores = self.features_data.sort_values('rank')
        
        return self.rice_scores
    
    def get_top_features(self, n: int = 3) -> pd.DataFrame:
        """
        Get top N prioritized features
        
        Args:
            n: Number of top features to return
            
        Returns:
            DataFrame with top N features
        """
        if self.rice_scores is None:
            self.prioritize_features()
        
        return self.rice_scores.head(n)
    
    def calculate_expected_impact(self, feature_row: pd.Series) -> Dict[str, float]:
        """
        Calculate expected business impact for a feature
        
        Args:
            feature_row: Single row from features DataFrame
            
        Returns:
            Dictionary with impact metrics
        """
        reach_users = feature_row['reach_users']
        impact_multiplier = feature_row['impact_score']
        confidence = feature_row['confidence_score']
        
        # Calculate metrics
        affected_orders = reach_users * AVERAGE_ORDERS_PER_MONTH
        order_increase_pct = impact_multiplier * 5  # 5% base increase per impact point
        additional_orders = affected_orders * (order_increase_pct / 100) * confidence
        revenue_impact = additional_orders * AVERAGE_ORDER_VALUE
        annual_revenue_impact = revenue_impact * 12
        
        return {
            'affected_users': reach_users,
            'affected_orders_monthly': affected_orders,
            'order_increase_pct': order_increase_pct,
            'additional_orders_monthly': additional_orders,
            'monthly_revenue_impact_inr': revenue_impact,
            'annual_revenue_impact_inr': annual_revenue_impact,
            'confidence_adjusted': confidence * 100
        }
    
    def generate_summary_report(self) -> str:
        """
        Generate text summary of prioritization results
        
        Returns:
            Formatted summary string
        """
        if self.rice_scores is None:
            self.prioritize_features()
        
        top_3 = self.get_top_features(3)
        
        report = "=" * 80 + "\n"
        report += "FEATURE PRIORITIZATION REPORT - RICE FRAMEWORK\n"
        report += "=" * 80 + "\n\n"
        
        report += f"Total Features Evaluated: {len(self.features_data)}\n"
        report += f"Business Context: {MONTHLY_ACTIVE_USERS:,} MAU\n"
        report += f"Average Order Value: ₹{AVERAGE_ORDER_VALUE}\n\n"
        
        report += "TOP 3 PRIORITIZED FEATURES:\n"
        report += "-" * 80 + "\n\n"
        
        for idx, (_, feature) in enumerate(top_3.iterrows(), 1):
            impact = self.calculate_expected_impact(feature)
            
            report += f"#{idx} - {feature['feature_name']}\n"
            report += f"   Category: {feature['category']}\n"
            report += f"   RICE Score: {feature['rice_score']:.2f}\n"
            report += f"   Reach: {feature['reach_users']:,.0f} users ({feature['reach_percentage']:.0f}% of MAU)\n"
            report += f"   Impact: {feature['impact_level']} ({feature['impact_score']}x)\n"
            report += f"   Confidence: {feature['confidence_level']} ({feature['confidence_score']*100:.0f}%)\n"
            report += f"   Effort: {feature['effort_months']} person-months\n"
            report += f"   \n"
            report += f"   Expected Impact:\n"
            report += f"   - Order Increase: {impact['order_increase_pct']:.1f}%\n"
            report += f"   - Additional Monthly Orders: {impact['additional_orders_monthly']:,.0f}\n"
            report += f"   - Monthly Revenue Impact: ₹{impact['monthly_revenue_impact_inr']:,.0f}\n"
            report += f"   - Annual Revenue Impact: ₹{impact['annual_revenue_impact_inr']:,.0f}\n"
            report += f"\n   Description: {feature['description']}\n"
            report += "\n" + "-" * 80 + "\n\n"
        
        return report


def create_sample_features() -> pd.DataFrame:
    """
    Create sample feature dataset for demonstration
    
    Returns:
        DataFrame with feature ideas
    """
    features = [
        {
            'feature_name': 'Smart Reorder',
            'category': 'Customer Retention',
            'description': 'One-tap reorder of previous favorite orders with smart suggestions',
            'reach_percentage': 65,
            'impact_level': 'High',
            'confidence_level': 'High',
            'effort_months': 2
        },
        {
            'feature_name': 'Group Ordering',
            'category': 'Order Value Increase',
            'description': 'Allow multiple users to add items to shared cart for office/group orders',
            'reach_percentage': 25,
            'impact_level': 'Massive',
            'confidence_level': 'Medium',
            'effort_months': 4
        },
        {
            'feature_name': 'Loyalty Gamification',
            'category': 'Customer Retention',
            'description': 'Points, badges, and tier system to reward frequent users',
            'reach_percentage': 80,
            'impact_level': 'Medium',
            'confidence_level': 'High',
            'effort_months': 3
        },
        {
            'feature_name': 'AI-Powered Search',
            'category': 'Discovery & Exploration',
            'description': 'Natural language search with contextual understanding',
            'reach_percentage': 90,
            'impact_level': 'Medium',
            'confidence_level': 'Low',
            'effort_months': 6
        },
        {
            'feature_name': 'Schedule Orders',
            'category': 'User Experience',
            'description': 'Pre-schedule orders for future delivery times',
            'reach_percentage': 40,
            'impact_level': 'High',
            'confidence_level': 'High',
            'effort_months': 1.5
        },
        {
            'feature_name': 'Live Order Tracking',
            'category': 'User Experience',
            'description': 'Real-time GPS tracking with delivery partner photo',
            'reach_percentage': 95,
            'impact_level': 'High',
            'confidence_level': 'Medium',
            'effort_months': 3
        },
        {
            'feature_name': 'Restaurant Stories',
            'category': 'Discovery & Exploration',
            'description': 'Instagram-style stories showing daily specials and new items',
            'reach_percentage': 50,
            'impact_level': 'Low',
            'confidence_level': 'Low',
            'effort_months': 2
        },
        {
            'feature_name': 'Split Payment',
            'category': 'User Experience',
            'description': 'Allow multiple payment methods for single order',
            'reach_percentage': 35,
            'impact_level': 'Medium',
            'confidence_level': 'High',
            'effort_months': 2
        },
        {
            'feature_name': 'Subscription Plans',
            'category': 'Customer Retention',
            'description': 'Monthly subscription for free delivery and exclusive discounts',
            'reach_percentage': 30,
            'impact_level': 'Massive',
            'confidence_level': 'Medium',
            'effort_months': 5
        },
        {
            'feature_name': 'Instant Checkout',
            'category': 'Operational Efficiency',
            'description': 'One-click checkout with saved preferences',
            'reach_percentage': 70,
            'impact_level': 'High',
            'confidence_level': 'High',
            'effort_months': 1
        },
        {
            'feature_name': 'Personalized Homepage',
            'category': 'Discovery & Exploration',
            'description': 'ML-powered homepage based on order history and preferences',
            'reach_percentage': 85,
            'impact_level': 'High',
            'confidence_level': 'Medium',
            'effort_months': 4
        },
        {
            'feature_name': 'Dietary Filters',
            'category': 'User Experience',
            'description': 'Filter restaurants and dishes by dietary preferences',
            'reach_percentage': 45,
            'impact_level': 'Medium',
            'confidence_level': 'High',
            'effort_months': 1.5
        },
        {
            'feature_name': 'Social Sharing',
            'category': 'Discovery & Exploration',
            'description': 'Share favorite dishes and restaurants on social media',
            'reach_percentage': 20,
            'impact_level': 'Low',
            'confidence_level': 'High',
            'effort_months': 1
        },
        {
            'feature_name': 'Contactless Delivery',
            'category': 'User Experience',
            'description': 'Leave at door option with photo confirmation',
            'reach_percentage': 60,
            'impact_level': 'Medium',
            'confidence_level': 'High',
            'effort_months': 0.5
        },
        {
            'feature_name': 'Dynamic Pricing',
            'category': 'Operational Efficiency',
            'description': 'Surge pricing during peak hours to manage demand',
            'reach_percentage': 100,
            'impact_level': 'High',
            'confidence_level': 'Low',
            'effort_months': 3
        }
    ]
    
    return pd.DataFrame(features)


if __name__ == "__main__":
    print("🚀 Running RICE Prioritization Framework...\n")
    
    # Create sample data
    features_df = create_sample_features()
    print(f"✅ Created {len(features_df)} feature ideas\n")
    
    # Initialize framework
    rice = RICEFramework(features_df)
    
    # Calculate prioritization
    results = rice.prioritize_features()
    
    # Generate report
    report = rice.generate_summary_report()
    print(report)
    
    # Save results
    results.to_csv(PROCESSED_DATA_DIR / 'rice_scores.csv', index=False)
    print(f"💾 Results saved to {PROCESSED_DATA_DIR / 'rice_scores.csv'}")