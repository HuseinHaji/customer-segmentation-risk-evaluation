"""
Engineer customer-level features for segmentation and risk analysis.

This module transforms raw customer data into business-relevant features:
- Payment behavior metrics
- Revenue and profitability ratios
- Credit exposure and utilization
- Customer value scores

Features are designed to be interpretable for business users.
"""

import numpy as np
import pandas as pd
from config import RAW_DIR, PROCESSED_DIR, PAYMENT_DELAY_BINS, PAYMENT_DELAY_LABELS


def engineer_payment_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer payment behavior features.

    Args:
        df: Raw customer dataframe

    Returns:
        DataFrame with payment features added
    """
    # Overdue ratio as percentage of annual revenue
    df["overdue_ratio"] = df["overdue_amount"] / (df["annual_revenue"] + 1e-6)
    df["overdue_ratio"] = df["overdue_ratio"].clip(0, 1)

    # Payment delay category for visualization
    df["payment_delay_category"] = pd.cut(
        df["payment_delay_days"],
        bins=PAYMENT_DELAY_BINS,
        labels=PAYMENT_DELAY_LABELS,
        include_lowest=True,
    )

    return df


def engineer_profitability_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer revenue and profitability features.

    Args:
        df: Dataframe with financial data

    Returns:
        DataFrame with profitability features added
    """
    # Revenue per order
    df["revenue_per_order"] = df["annual_revenue"] / (df["number_of_orders"] + 1)
    df["invoice_count"] = df.get("invoice_count", df["number_of_orders"])
    df["product_count"] = df.get("product_count", 1)

    # Gross profit in absolute terms
    df["gross_profit"] = df["annual_revenue"] * df["gross_margin"]

    # Annual gross profit
    df["annual_gross_profit"] = df["gross_profit"]

    return df


def engineer_credit_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer credit exposure and utilization features.

    Args:
        df: Dataframe with credit and exposure data

    Returns:
        DataFrame with credit features added
    """
    # Exposure as percentage of credit limit
    df["exposure_utilization"] = df["current_exposure"] / (df["credit_limit"] + 1e-6)
    df["exposure_utilization"] = df["exposure_utilization"].clip(0, 2)  # Cap at 200%

    # Exposure at risk (considering overdue amounts)
    df["exposure_at_risk"] = df["current_exposure"] + df["overdue_amount"]

    return df


def engineer_customer_health_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer customer health and relationship metrics.

    Args:
        df: Dataframe with customer relationship data

    Returns:
        DataFrame with health metrics added
    """
    # Relationship maturity (in years)
    df["relationship_years"] = df["relationship_length_months"] / 12

    # Invoice consistency (orders per month of relationship)
    df["order_frequency"] = df["number_of_orders"] / (df["relationship_length_months"] + 1)

    return df


def engineer_risk_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer risk indication features.

    Args:
        df: Dataframe with behavior data

    Returns:
        DataFrame with risk indicators added
    """
    # Binary default flag if not present
    if "default_flag" not in df.columns:
        df["default_flag"] = 0

    # Concentration risk (% of revenue with high delay)
    high_delay_revenue = df[df["payment_delay_days"] > 30]["annual_revenue"].sum()
    total_revenue = df["annual_revenue"].sum()
    df["high_payment_delay_concentration"] = high_delay_revenue / total_revenue if total_revenue > 0 else 0

    return df


def main() -> None:
    """Load raw data, engineer features, and save processed dataset."""
    print("Loading raw customer data...")
    customers = pd.read_csv(RAW_DIR / "customer_master.csv")

    print("Engineering payment metrics...")
    customers = engineer_payment_metrics(customers)

    print("Engineering profitability metrics...")
    customers = engineer_profitability_metrics(customers)

    print("Engineering credit metrics...")
    customers = engineer_credit_metrics(customers)

    print("Engineering customer health metrics...")
    customers = engineer_customer_health_metrics(customers)

    print("Engineering risk indicators...")
    customers = engineer_risk_indicators(customers)

    # Ensure output directory exists
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Save engineered features
    output_file = PROCESSED_DIR / "customer_features.csv"
    customers.to_csv(output_file, index=False)

    print(f"✓ Customer features engineered and saved: {output_file}")
    print(f"  - {len(customers)} customer records")
    print(f"  - {customers.shape[1]} features")


if __name__ == "__main__":
    main()
