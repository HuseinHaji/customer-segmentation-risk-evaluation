"""
Export BI-ready customer dataset for Power BI visualization and reporting.

This module creates a flat, denormalized dataset optimized for Power BI:
- Clean column names
- Business-readable categories
- All relevant customer, segment, risk, and performance metrics
- No null values (imputed with defaults)
- Dashboard-ready format

The output is designed for:
1. Executive overview dashboards
2. Segment analysis reports
3. Risk evaluation views
4. Customer drilldown functionality
5. Geographic and industry analysis
"""

import pandas as pd
import numpy as np
from config import PROCESSED_DIR, POWERBI_DIR, POWERBI_DASHBOARD_FILE, DASHBOARD_COLORS


def clean_for_powerbi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare dataset for Power BI.

    Args:
        df: Customer dataframe with all metrics

    Returns:
        BI-ready dataframe
    """
    # Fill missing values
    df = df.fillna(0)

    # Round numerical columns for readability
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if "ratio" in col or "margin" in col or "score" in col or "probability" in col:
            df[col] = df[col].round(4)
        elif "days" in col or "delay" in col:
            df[col] = df[col].round(1)
        elif "revenue" in col or "exposure" in col or "profit" in col or "amount" in col:
            df[col] = df[col].round(2)

    return df


def select_powerbi_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Select and rename columns for BI dashboard.

    Returns:
        Dataframe with BI-optimized columns
    """
    # Column mapping: source -> BI-ready name
    column_mapping = {
        "customer_id": "Customer ID",
        "country": "Country",
        "industry": "Industry",
        "company_size": "Company Size",
        "annual_revenue": "Annual Revenue (€)",
        "gross_margin": "Gross Margin",
        "number_of_orders": "Number of Orders",
        "avg_invoice_value": "Avg Invoice Value (€)",
        "payment_delay_days": "Avg Payment Delay (Days)",
        "overdue_amount": "Overdue Amount (€)",
        "overdue_ratio": "Overdue Ratio",
        "payment_delay_category": "Payment Status",
        "product_category": "Product Category",
        "credit_limit": "Credit Limit (€)",
        "current_exposure": "Current Exposure (€)",
        "exposure_utilization": "Exposure Utilization %",
        "exposure_at_risk": "Exposure at Risk (€)",
        "relationship_length_months": "Relationship (Months)",
        "relationship_years": "Relationship (Years)",
        "order_frequency": "Order Frequency (Orders/Month)",
        "default_flag": "Prior Default Flag",
        "gross_profit": "Gross Profit (€)",
        "revenue_per_order": "Revenue per Order (€)",
        "segment_name": "Segment",
        "segment_description": "Segment Description",
        "segment_priority": "Segment Priority",
        "risk_score": "Risk Score",
        "risk_category": "Risk Category",
        "risk_band": "Risk Band",
        "default_probability_proxy": "Default Probability Estimate",
        "payment_behavior_score": "Payment Behavior Score (0-10)",
        "profitability_score": "Profitability Score (0-10)",
        "commercial_value_score": "Commercial Value Score (0-10)",
    }

    # Select available columns
    available_cols = [col for col in column_mapping.keys() if col in df.columns]
    df_powerbi = df[available_cols].copy()

    # Rename for BI
    df_powerbi.rename(columns={col: column_mapping[col] for col in available_cols}, inplace=True)

    # Reorder columns logically
    col_order = [
        "Customer ID",
        "Country",
        "Industry",
        "Company Size",
        "Segment",
        "Segment Description",
        "Segment Priority",
        "Annual Revenue (€)",
        "Gross Margin",
        "Gross Profit (€)",
        "Number of Orders",
        "Avg Invoice Value (€)",
        "Revenue per Order (€)",
        "Order Frequency (Orders/Month)",
        "Product Category",
        "Risk Category",
        "Risk Score",
        "Risk Band",
        "Default Probability Estimate",
        "Avg Payment Delay (Days)",
        "Payment Status",
        "Overdue Amount (€)",
        "Overdue Ratio",
        "Payment Behavior Score (0-10)",
        "Credit Limit (€)",
        "Current Exposure (€)",
        "Exposure Utilization %",
        "Exposure at Risk (€)",
        "Commercial Value Score (0-10)",
        "Profitability Score (0-10)",
        "Relationship (Months)",
        "Relationship (Years)",
        "Prior Default Flag",
    ]

    # Keep only columns that exist
    col_order = [col for col in col_order if col in df_powerbi.columns]
    df_powerbi = df_powerbi[col_order]

    return df_powerbi


def add_powerbi_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Power BI-specific helper columns for visualization.

    Args:
        df: Dataframe with core metrics

    Returns:
        Dataframe with BI visualization columns
    """
    # Revenue size bucket for filtering/grouping
    if "Annual Revenue (€)" in df.columns:
        df["Revenue Size"] = pd.cut(
            df["Annual Revenue (€)"],
            bins=[0, 250000, 500000, 1000000, 2000000],
            labels=["<250K", "250K-500K", "500K-1M", ">1M"],
        )

    # Exposure utilization bucket
    if "Exposure Utilization %" in df.columns:
        df["Utilization Level"] = pd.cut(
            df["Exposure Utilization %"],
            bins=[0, 0.33, 0.67, 1.0, 2.0],
            labels=["Low", "Moderate", "High", "Over-Utilized"],
        )

    # Payment delay bucket
    if "Avg Payment Delay (Days)" in df.columns:
        df["Payment Timeliness"] = pd.cut(
            df["Avg Payment Delay (Days)"],
            bins=[-1, 7, 14, 30, 100],
            labels=["On Time", "Slightly Late", "Late", "Very Late"],
        )

    return df


def main() -> None:
    """
    Load customer data with all metrics and export BI-ready dataset.
    """
    print("Loading customer features...")
    features = pd.read_csv(PROCESSED_DIR / "customer_features.csv")

    print("Loading customer segments...")
    segments = pd.read_csv(PROCESSED_DIR / "customer_segments.csv")

    print("Loading risk scores...")
    risk = pd.read_csv(PROCESSED_DIR / "risk_scored_customers.csv")

    # Merge all datasets
    print("Merging datasets...")
    segment_cols = [
        "customer_id",
        "segment_id",
        "segment_name",
        "segment_description",
        "segment_priority",
        "main_risk_driver",
        "commercial_action",
    ]
    risk_cols = [
        "customer_id",
        "risk_score",
        "risk_category",
        "risk_band",
        "default_probability_proxy",
        "payment_behavior_score",
        "profitability_score",
        "commercial_value_score",
    ]
    df = features.drop(
        columns=[col for col in segment_cols + risk_cols if col != "customer_id" and col in features.columns],
        errors="ignore",
    )
    df = df.merge(segments[[col for col in segment_cols if col in segments.columns]], on="customer_id", how="left")
    df = df.merge(risk[[col for col in risk_cols if col in risk.columns]], on="customer_id", how="left")

    # Clean for Power BI
    print("Preparing for Power BI...")
    df = clean_for_powerbi(df)
    df = select_powerbi_columns(df)
    df = add_powerbi_features(df)

    # Create output directory
    POWERBI_DIR.mkdir(parents=True, exist_ok=True)

    # Save BI-ready export
    df.to_csv(POWERBI_DASHBOARD_FILE, index=False)
    print(f"✓ Power BI export created: {POWERBI_DASHBOARD_FILE}")
    print(f"  - {len(df)} customer records")
    print(f"  - {df.shape[1]} dimensions and measures")
    print(f"\nReady for Power BI, Tableau, or other BI platforms.")
    print(f"\nSuggested dashboard pages:")
    print(f"  1. Executive Overview (KPIs: Revenue, Customers, Risk Distribution)")
    print(f"  2. Segment Analysis (Segment breakdown by revenue, risk, margin)")
    print(f"  3. Risk Evaluation (Risk distribution, exposure analysis)")
    print(f"  4. Revenue & Margin (By segment, by industry, by country)")
    print(f"  5. Customer Drilldown (Interactive customer lookup)")


if __name__ == "__main__":
    main()
