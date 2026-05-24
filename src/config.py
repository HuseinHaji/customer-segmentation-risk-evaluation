"""
Configuration and constants for Customer Segmentation & Risk Evaluation project.

This module centralizes all paths, constants, and parameters used across the pipeline.
"""

from pathlib import Path

# ============================================================================
# PROJECT DIRECTORIES
# ============================================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
POWERBI_DIR = DATA_DIR / "powerbi"
OUTPUT_DIR = ROOT_DIR / "output"
SQL_DIR = ROOT_DIR / "sql"

# Create output directories if they don't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)
POWERBI_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# RANDOM SEED AND DATA GENERATION PARAMETERS
# ============================================================================

RANDOM_SEED = 42  # Ensures reproducibility across all synthetic data generation
CUSTOMER_COUNT = 150  # Total number of synthetic customers to generate

# ============================================================================
# CUSTOMER MASTER DATA PARAMETERS
# ============================================================================

COUNTRIES = ["Germany", "France", "Italy", "Netherlands", "Austria", "Belgium", "Spain"]
INDUSTRIES = ["Automotive", "Pharma", "FMCG", "Logistics", "Retail", "Chemicals", "Electronics"]
PRODUCT_CATEGORIES = ["Machinery", "Software", "Chemicals", "Packaging", "Components"]
COMPANY_SIZES = ["SME", "Mid-Market", "Enterprise"]

# Revenue generation parameters (in €)
REVENUE_MEAN = 850000
REVENUE_STD = 280000
REVENUE_MIN = 50000

# Margin parameters
MARGIN_MEAN = 0.16
MARGIN_STD = 0.06
MARGIN_MIN = 0.02
MARGIN_MAX = 0.40

# Payment behavior parameters
PAYMENT_DELAY_MEAN = 12  # days
PAYMENT_DELAY_STD = 9
PAYMENT_DELAY_MIN = 0

# Credit and exposure parameters
OVERDUE_RATIO_MIN = 0.0
OVERDUE_RATIO_MAX = 0.08
CREDIT_LIMIT_MIN_MULT = 0.45  # as multiple of revenue
CREDIT_LIMIT_MAX_MULT = 0.90
EXPOSURE_AMOUNT_MIN_MULT = 0.25  # as multiple of revenue
EXPOSURE_AMOUNT_MAX_MULT = 0.75

# Default probability (8% baseline)
DEFAULT_PROBABILITY = 0.08

# Tenure and order parameters
TENURE_MONTHS_MIN = 6
TENURE_MONTHS_MAX = 96
ORDER_COUNT_POISSON_LAMBDA = 18
ORDER_COUNT_MIN = 3

# ============================================================================
# SEGMENTATION PARAMETERS
# ============================================================================

N_CLUSTERS = 6  # Number of technical clusters used as a supporting signal
SEGMENTATION_SEED = 42

# Segment definitions (business-readable names and descriptions)
SEGMENT_DEFINITIONS = {
    "Strategic High-Value Customers": {
        "description": "High revenue, excellent payment history, strategic importance",
        "priority": "CRITICAL",
        "main_risk_driver": "Concentration risk",
        "commercial_action": "Dedicated account management, cross-sell opportunities",
    },
    "Stable Low-Risk Customers": {
        "description": "Consistent revenue, predictable payment, low default risk",
        "priority": "MAINTAIN",
        "main_risk_driver": "Limited growth potential",
        "commercial_action": "Regular engagement, loyalty programs",
    },
    "Growth Potential Customers": {
        "description": "Above-average revenue with moderate risk profile",
        "priority": "DEVELOP",
        "main_risk_driver": "Payment behavior volatility",
        "commercial_action": "Expansion opportunities, credit line review",
    },
    "Late-Paying Watchlist": {
        "description": "Acceptable revenue but concerning payment delays",
        "priority": "MONITOR",
        "main_risk_driver": "Payment delay and working capital issues",
        "commercial_action": "Credit tightening, enhanced collection procedures",
    },
    "High-Risk Low-Margin Customers": {
        "description": "Limited profitability combined with elevated risk",
        "priority": "RESTRICT",
        "main_risk_driver": "Low margin and payment inconsistency",
        "commercial_action": "Pricing review, reduce exposure, or exit",
    },
    "New / Limited-History Customers": {
        "description": "Short relationship history with limited behavioral evidence",
        "priority": "REVIEW",
        "main_risk_driver": "Limited performance history",
        "commercial_action": "Controlled onboarding, smaller exposure increases",
    },
}

# ============================================================================
# RISK SCORING PARAMETERS
# ============================================================================

# Risk score components and weights
RISK_SCORE_WEIGHTS = {
    "overdue_ratio": 8.0,  # Heavy weight on current overdue amount
    "payment_delay_days": 1.0,  # ~1 point per 30 days
    "margin_quality": 2.5,  # Low margin shortfall = higher risk
    "default_flag": 15.0,  # Prior default is very serious
    "exposure_utilization": 2.0,  # Higher utilization = more risk
    "relationship_length": -0.1,  # Longer relationship reduces risk slightly
}

# Risk categories and thresholds
RISK_CATEGORIES = {
    "Low Risk": {"min": 0, "max": 2.5, "color": "green"},
    "Medium Risk": {"min": 2.5, "max": 5.0, "color": "yellow"},
    "Elevated Risk": {"min": 5.0, "max": 8.0, "color": "orange"},
    "High Risk": {"min": 8.0, "max": float("inf"), "color": "red"},
}

# ============================================================================
# FEATURE ENGINEERING PARAMETERS
# ============================================================================

# Quartile thresholds for categorization
PAYMENT_DELAY_BINS = [-1, 7, 14, 30, 90]  # On time, Moderate, Delayed, High Delay
PAYMENT_DELAY_LABELS = ["On Time", "Moderate Delay", "Delayed", "High Delay"]

# ============================================================================
# OUTPUT FILE NAMES
# ============================================================================

CUSTOMER_MASTER_FILE = RAW_DIR / "customer_master.csv"
CUSTOMER_FEATURES_FILE = PROCESSED_DIR / "customer_features.csv"
CUSTOMER_SEGMENTS_FILE = PROCESSED_DIR / "customer_segments.csv"
RISK_SCORED_CUSTOMERS_FILE = PROCESSED_DIR / "risk_scored_customers.csv"
SEGMENT_SUMMARY_FILE = PROCESSED_DIR / "segment_summary.csv"
POWERBI_DASHBOARD_FILE = POWERBI_DIR / "powerbi_customer_dashboard.csv"

# ============================================================================
# DISPLAY SETTINGS FOR STREAMLIT AND REPORTS
# ============================================================================

CURRENCY = "€"
DECIMAL_PLACES = 2

# Dashboard color scheme
DASHBOARD_COLORS = {
    "Strategic High-Value": "#006400",  # Dark green
    "Stable Low-Risk": "#4CAF50",  # Light green
    "Growth Potential": "#2196F3",  # Blue
    "Late-Paying Watchlist": "#FF9800",  # Orange
    "High-Risk Low-Margin": "#F44336",  # Red
}

# ============================================================================
# DISCLAIMER
# ============================================================================

DISCLAIMER = (
    "This project uses fully synthetic customer data created for portfolio demonstration purposes. "
    "It does not contain real company data, proprietary information, or actual customer information. "
    "Risk scores are illustrative only and should not be used for actual credit decisions."
)
