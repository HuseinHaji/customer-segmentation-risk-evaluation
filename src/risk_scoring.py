"""
Risk scoring for customer portfolio evaluation.

This module computes a composite risk score for each customer based on:
- Payment behavior (delays, overdue amounts)
- Exposure metrics (utilization, concentration)
- Profitability (margin quality)
- Default history
- Relationship strength (tenure)

IMPORTANT: This is a synthetic scoring framework for portfolio demonstration purposes.
It is NOT a regulated credit risk model and should not be used for actual credit decisions.
For production use, scores should be validated against regulatory requirements and
historical default patterns.

Risk score interpretation:
  - 0-2.5:   Low Risk      - Strong payment history, low utilization, healthy margin
  - 2.5-5.0: Medium Risk   - Acceptable payment behavior, normal utilization
  - 5.0-8.0: Elevated Risk - Notable payment delays, higher utilization, margin concerns
  - 8.0+:    High Risk     - Serious payment issues, high utilization, low margin
"""

import numpy as np
import pandas as pd
from config import (
    PROCESSED_DIR,
    RISK_SCORE_WEIGHTS,
    RISK_CATEGORIES,
    CUSTOMER_FEATURES_FILE,
    CUSTOMER_SEGMENTS_FILE,
    RISK_SCORED_CUSTOMERS_FILE,
    SEGMENT_SUMMARY_FILE,
)


def compute_composite_risk_score(df: pd.DataFrame) -> pd.Series:
    """
    Compute composite risk score combining multiple risk factors.

    Risk score formula:
      score = (overdue_ratio * 8) + (payment_delay / 30) + margin shortfall
              + (default_flag * 15) + (exposure_util * 2) - (tenure_years * 0.1)

    Each component represents a specific risk dimension:
    - Overdue ratio (8x weight): Current payment delinquency
    - Payment delay (1/30 weight): Days of average payment deferral
    - Margin quality: margin below 20% increases risk in a capped, explainable way
    - Default flag (15x weight): Historical payment default is serious signal
    - Exposure utilization (2x weight): Higher utilization increases loss given default
    - Relationship tenure (-0.1x weight): Longer relationships are slightly lower risk

    Args:
        df: Customer dataframe with engineered features

    Returns:
        Series of risk scores
    """
    # Ensure required columns exist
    required_cols = ["overdue_ratio", "payment_delay_days", "gross_margin", "exposure_utilization"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = 0

    # Component scores
    overdue_component = df["overdue_ratio"] * RISK_SCORE_WEIGHTS["overdue_ratio"]
    delay_component = (df["payment_delay_days"] / 30) * RISK_SCORE_WEIGHTS["payment_delay_days"]
    margin_shortfall = ((0.20 - df["gross_margin"]).clip(lower=0) / 0.20).clip(0, 1)
    margin_component = margin_shortfall * RISK_SCORE_WEIGHTS["margin_quality"]
    default_component = df.get("default_flag", 0).astype(int) * RISK_SCORE_WEIGHTS["default_flag"]
    utilization_component = (
        df["exposure_utilization"] * RISK_SCORE_WEIGHTS["exposure_utilization"]
    )
    tenure_component = (
        df.get("relationship_years", 0) * RISK_SCORE_WEIGHTS["relationship_length"]
    )

    # Composite score
    risk_score = (
        overdue_component
        + delay_component
        + margin_component
        + default_component
        + utilization_component
        + tenure_component
    )

    return risk_score


def assign_risk_category(score: float) -> str:
    """
    Assign risk category based on score.

    Args:
        score: Numeric risk score

    Returns:
        Risk category label
    """
    for category, bounds in RISK_CATEGORIES.items():
        if bounds["min"] <= score < bounds["max"]:
            return category
    return "High Risk"  # Default to highest risk


def assign_risk_band(score: float) -> str:
    """
    Assign risk band for quartile distribution.

    Args:
        score: Numeric risk score

    Returns:
        Risk band label (Band 1-4)
    """
    if score < 2.5:
        return "Band 1 (Low)"
    elif score < 5.0:
        return "Band 2 (Medium)"
    elif score < 8.0:
        return "Band 3 (Elevated)"
    else:
        return "Band 4 (High)"


def main() -> None:
    """
    Load customer segments and features, compute risk scores, and save results.
    """
    print("Loading customer features...")
    features = pd.read_csv(CUSTOMER_FEATURES_FILE)

    print("Loading customer segments...")
    segments = pd.read_csv(CUSTOMER_SEGMENTS_FILE)

    # Merge features with segments
    segment_cols = [
        "customer_id",
        "segment_id",
        "segment_name",
        "segment_description",
        "segment_priority",
        "main_risk_driver",
        "commercial_action",
    ]
    customers = features.drop(
        columns=[col for col in segment_cols if col != "customer_id" and col in features.columns],
        errors="ignore",
    ).merge(
        segments[[col for col in segment_cols if col in segments.columns]],
        on="customer_id",
        how="left",
    )

    print("Computing composite risk scores...")
    customers["risk_score"] = compute_composite_risk_score(customers)

    print("Assigning risk categories...")
    customers["risk_category"] = customers["risk_score"].apply(assign_risk_category)
    customers["risk_band"] = customers["risk_score"].apply(assign_risk_band)

    # Estimate default probability (synthetic proxy)
    customers["default_probability_proxy"] = (customers["risk_score"] / 20).clip(0, 1)

    # Exposure at risk metrics
    customers["exposure_at_risk"] = customers["current_exposure"] + customers["overdue_amount"]

    # Payment behavior score (inverse of risk from payment perspective)
    customers["payment_behavior_score"] = (10 - customers["payment_delay_days"] / 3).clip(0, 10)

    # Profitability score
    customers["profitability_score"] = (
        customers["gross_margin"] * 10 + customers["annual_revenue"] / 100000
    ).clip(0, 10)

    # Commercial value score (combining revenue and margin)
    customers["commercial_value_score"] = (
        (customers["annual_revenue"] / 1000000) * 10 + customers["gross_margin"] * 5
    ).clip(0, 10)

    # Save risk-scored customer file
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    risk_cols = [
        "customer_id",
        "country",
        "industry",
        "annual_revenue",
        "gross_margin",
        "segment_name",
        "segment_id",
        "risk_score",
        "risk_category",
        "risk_band",
        "default_probability_proxy",
        "exposure_at_risk",
        "overdue_ratio",
        "payment_behavior_score",
        "profitability_score",
        "commercial_value_score",
    ]

    risk_output = customers[[col for col in risk_cols if col in customers.columns]]
    risk_output.to_csv(RISK_SCORED_CUSTOMERS_FILE, index=False)
    print(f"✓ Risk scores computed and saved: {RISK_SCORED_CUSTOMERS_FILE}")

    # Create final enriched customer_features.csv for end-to-end analytics
    enriched_columns = [
        "customer_id",
        "country",
        "industry",
        "company_size",
        "annual_revenue",
        "gross_margin",
        "gross_profit",
        "annual_gross_profit",
        "number_of_orders",
        "invoice_count",
        "avg_invoice_value",
        "revenue_per_order",
        "product_count",
        "product_category",
        "payment_delay_days",
        "payment_delay_category",
        "overdue_amount",
        "overdue_ratio",
        "credit_limit",
        "current_exposure",
        "exposure_utilization",
        "order_frequency",
        "relationship_length_months",
        "relationship_years",
        "default_flag",
        "risk_score",
        "risk_category",
        "risk_band",
        "default_probability_proxy",
        "exposure_at_risk",
        "payment_behavior_score",
        "profitability_score",
        "commercial_value_score",
        "segment_id",
        "segment_name",
        "segment_description",
        "segment_priority",
        "main_risk_driver",
        "commercial_action",
    ]
    enriched_features = customers[[col for col in enriched_columns if col in customers.columns]].copy()
    enriched_features.to_csv(CUSTOMER_FEATURES_FILE, index=False)
    print(f"✓ Enriched customer features saved: {CUSTOMER_FEATURES_FILE}")

    # Compute segment-level summary
    print("Computing segment-level summary...")
    segment_summary = customers.groupby("segment_name", as_index=False).agg(
        segment_id=("segment_id", "first"),
        number_of_customers=("customer_id", "count"),
        total_revenue=("annual_revenue", "sum"),
        total_exposure=("exposure_at_risk", "sum"),
        avg_margin=("gross_margin", "mean"),
        avg_payment_delay=("payment_delay_days", "mean"),
        overdue_amount=("overdue_amount", "sum"),
        high_risk_customer_share=(
            "risk_category",
            lambda x: (x.isin(["Elevated Risk", "High Risk"])).sum() / len(x),
        ),
        default_rate=("default_flag", "mean"),
        exposure_utilization=("exposure_utilization", "mean"),
    )
    segment_summary = segment_summary[
        [
            "segment_id",
            "segment_name",
            "number_of_customers",
            "total_revenue",
            "total_exposure",
            "avg_margin",
            "avg_payment_delay",
            "overdue_amount",
            "high_risk_customer_share",
            "default_rate",
            "exposure_utilization",
        ]
    ]

    # Add recommended actions based on risk profile
    def recommend_action(row):
        if row["high_risk_customer_share"] > 0.5:
            return "Restrict exposure, enhanced monitoring"
        elif row["avg_payment_delay"] > 20:
            return "Collection focus, credit line review"
        elif row["default_rate"] > 0.1:
            return "Portfolio reduction, exit planning"
        else:
            return "Maintain engagement, growth opportunities"

    segment_summary["recommended_action"] = segment_summary.apply(recommend_action, axis=1)

    segment_summary.to_csv(SEGMENT_SUMMARY_FILE, index=False)
    print(f"✓ Segment summary saved: {SEGMENT_SUMMARY_FILE}")

    # Print summary statistics
    print("\nRisk Score Distribution:")
    print(customers["risk_category"].value_counts().to_string())
    print(f"\nAverage Risk Score: {customers['risk_score'].mean():.2f}")
    print(f"Median Risk Score: {customers['risk_score'].median():.2f}")
    print(f"High Risk Customers: {(customers['risk_category'] == 'High Risk').sum()} ({100 * (customers['risk_category'] == 'High Risk').mean():.1f}%)")


if __name__ == "__main__":
    main()
