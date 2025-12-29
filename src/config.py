"""
Configuration file for Feature Prioritization Framework
Author: Ayush Saxena
Date: December 2025
"""

import os
from pathlib import Path

# Project Root
PROJECT_ROOT = Path(__file__).parent.parent

# Directory Paths
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"
REPORTS_DIR = OUTPUT_DIR / "reports"

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, SYNTHETIC_DATA_DIR, 
                  FIGURES_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Business Metrics
MONTHLY_ACTIVE_USERS = 500000
AVERAGE_ORDER_VALUE = 350  # INR
AVERAGE_ORDERS_PER_MONTH = 2.5
CUSTOMER_LIFETIME_MONTHS = 24

# RICE Framework Weights
RICE_WEIGHTS = {
    'reach': 0.3,
    'impact': 0.3,
    'confidence': 0.2,
    'effort': 0.2
}

# A/B Test Configuration
AB_TEST_CONFIG = {
    'significance_level': 0.05,  # 95% confidence
    'statistical_power': 0.8,
    'minimum_detectable_effect': 0.05,  # 5% lift
    'test_duration_days': 14,
    'control_variant_ratio': 0.5  # 50-50 split
}

# Feature Categories
FEATURE_CATEGORIES = [
    'Customer Retention',
    'Order Value Increase',
    'Operational Efficiency',
    'User Experience',
    'Discovery & Exploration'
]

# Impact Scale (1-3)
IMPACT_SCALE = {
    'Massive': 3,
    'High': 2,
    'Medium': 1,
    'Low': 0.5,
    'Minimal': 0.25
}

# Confidence Scale (Percentage)
CONFIDENCE_SCALE = {
    'High': 100,
    'Medium': 80,
    'Low': 50
}

# Color Scheme for Visualizations
COLOR_SCHEME = {
    'primary': '#FF6B6B',
    'secondary': '#4ECDC4',
    'accent': '#FFE66D',
    'success': '#95E1D3',
    'warning': '#F38181'
}

print(f"✅ Configuration loaded successfully")
print(f"📁 Project Root: {PROJECT_ROOT}")
