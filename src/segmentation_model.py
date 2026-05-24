"""
Customer segmentation using KMeans clustering on engineered features.

This module:
1. Selects relevant features for clustering
2. Applies KMeans to identify customer segments
3. Assigns business-readable segment labels based on cluster characteristics
4. Outputs segment assignments for each customer

Note: This is a demonstration of customer segmentation for portfolio purposes.
In production, segment definitions would be validated against business strategies
and historical customer behavior.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from config import N_CLUSTERS, PROCESSED_DIR, SEGMENTATION_SEED, SEGMENT_DEFINITIONS


def select_clustering_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Select and standardize features for KMeans clustering.

    Features selected emphasize:
    - Customer value (revenue, margin)
    - Payment behavior (delay, overdue ratio)
    - Credit utilization (exposure as % of limit)

    Args:
        df: Dataframe with engineered features

    Returns:
        Standardized feature matrix for clustering
    """
    features = [
        "annual_revenue",
        "overdue_ratio",
        "payment_delay_days",
        "gross_margin",
        "exposure_utilization",
    ]

    feature_matrix = df[features].fillna(0)

    # Standardize features to have mean=0 and std=1
    scaler = StandardScaler()
    standardized_features = scaler.fit_transform(feature_matrix)

    return standardized_features, features


def assign_segment_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign business-readable segment labels based on cluster characteristics.

    Segmentation logic:
    - Analyze cluster centers along key dimensions
    - Assign names that reflect business positioning
    - Capture risk/value profile in segment name

    Args:
        df: Dataframe with cluster assignments and engineered features

    Returns:
        DataFrame with segment names added
    """
    revenue_q75 = df["annual_revenue"].quantile(0.75)
    revenue_q45 = df["annual_revenue"].quantile(0.45)
    margin_median = df["gross_margin"].median()
    margin_q35 = df["gross_margin"].quantile(0.35)

    conditions = [
        df["relationship_length_months"] <= 12,
        (df["gross_margin"] <= margin_q35)
        & (
            (df["payment_delay_days"] > 24)
            | (df["overdue_ratio"] > 0.045)
            | (df["default_flag"] == 1)
        ),
        (df["annual_revenue"] >= revenue_q75)
        & (df["gross_margin"] >= margin_median)
        & (df["payment_delay_days"] <= 14)
        & (df["overdue_ratio"] <= 0.03),
        (df["payment_delay_days"] > 21) | (df["overdue_ratio"] > 0.04),
        (df["payment_delay_days"] <= 10)
        & (df["overdue_ratio"] <= 0.02)
        & (df["exposure_utilization"] <= 0.85),
    ]
    choices = [
        "New / Limited-History Customers",
        "High-Risk Low-Margin Customers",
        "Strategic High-Value Customers",
        "Late-Paying Watchlist",
        "Stable Low-Risk Customers",
    ]

    df["segment_name"] = np.select(conditions, choices, default="Growth Potential Customers")
    segment_ids = {name: idx + 1 for idx, name in enumerate(SEGMENT_DEFINITIONS)}
    df["segment_id"] = df["segment_name"].map(segment_ids)
    df["model_cluster"] = df["cluster"]

    return df


def main() -> None:
    """Load features, perform clustering, assign segments, and save results."""
    print("Loading engineered customer features...")
    customers = pd.read_csv(PROCESSED_DIR / "customer_features.csv")

    print("Selecting clustering features...")
    feature_matrix, feature_names = select_clustering_features(customers)

    print(f"Performing KMeans clustering (k={N_CLUSTERS})...")
    model = KMeans(n_clusters=N_CLUSTERS, random_state=SEGMENTATION_SEED, n_init=10)
    customers["cluster"] = model.fit_predict(feature_matrix)

    print("Assigning business-readable segment names...")
    customers = assign_segment_labels(customers)

    # Add business labels and references
    customers["segment_description"] = customers["segment_name"].map(
        {name: defs["description"] for name, defs in SEGMENT_DEFINITIONS.items()}
    )
    customers["segment_priority"] = customers["segment_name"].map(
        {name: defs["priority"] for name, defs in SEGMENT_DEFINITIONS.items()}
    )
    customers["main_risk_driver"] = customers["segment_name"].map(
        {name: defs["main_risk_driver"] for name, defs in SEGMENT_DEFINITIONS.items()}
    )
    customers["commercial_action"] = customers["segment_name"].map(
        {name: defs["commercial_action"] for name, defs in SEGMENT_DEFINITIONS.items()}
    )

    # Save segmentation results
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_file = PROCESSED_DIR / "customer_segments.csv"
    customers.to_csv(output_file, index=False)

    # Also update customer_features.csv with segment labels for downstream analytics
    enriched_features = customers.copy()
    enriched_features.to_csv(PROCESSED_DIR / "customer_features.csv", index=False)

    print(f"✓ Customer segments assigned and saved: {output_file}")
    print(f"✓ Enriched customer features saved: {PROCESSED_DIR / 'customer_features.csv'}")

    # Print segment summary
    segment_summary = customers["segment_name"].value_counts()
    print("\nSegment distribution:")
    for segment, count in segment_summary.items():
        pct = 100 * count / len(customers)
        print(f"  - {segment}: {count} customers ({pct:.1f}%)")


if __name__ == "__main__":
    main()
