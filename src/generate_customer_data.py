"""
Generate synthetic customer master data for portfolio demonstration.

This script creates a realistic synthetic B2B customer portfolio with:
- Customer demographics (country, industry)
- Revenue and margin metrics
- Payment behavior (delays, overdue amounts)
- Credit exposure and limits
- Default history flags

All data is deterministically generated using a fixed random seed for reproducibility.
"""

import numpy as np
import pandas as pd
from config import (
    RAW_DIR,
    RANDOM_SEED,
    CUSTOMER_COUNT,
    COUNTRIES,
    INDUSTRIES,
    PRODUCT_CATEGORIES,
    COMPANY_SIZES,
    REVENUE_MEAN,
    REVENUE_STD,
    REVENUE_MIN,
    MARGIN_MEAN,
    MARGIN_STD,
    MARGIN_MIN,
    MARGIN_MAX,
    PAYMENT_DELAY_MEAN,
    PAYMENT_DELAY_STD,
    PAYMENT_DELAY_MIN,
    OVERDUE_RATIO_MIN,
    OVERDUE_RATIO_MAX,
    CREDIT_LIMIT_MIN_MULT,
    CREDIT_LIMIT_MAX_MULT,
    EXPOSURE_AMOUNT_MIN_MULT,
    EXPOSURE_AMOUNT_MAX_MULT,
    DEFAULT_PROBABILITY,
    TENURE_MONTHS_MIN,
    TENURE_MONTHS_MAX,
    ORDER_COUNT_POISSON_LAMBDA,
    ORDER_COUNT_MIN,
)


def generate_customer_master() -> pd.DataFrame:
    """
    Generate synthetic customer master dataset.

    Returns:
        pd.DataFrame: Customer records with demographics, financials, and payment behavior.
    """
    rng = np.random.default_rng(RANDOM_SEED)
    customers = []

    for i in range(1, CUSTOMER_COUNT + 1):
        # Financial metrics
        revenue = max(REVENUE_MIN, abs(rng.normal(REVENUE_MEAN, REVENUE_STD)))
        margin = np.clip(rng.normal(MARGIN_MEAN, MARGIN_STD), MARGIN_MIN, MARGIN_MAX)

        # Order behavior
        number_of_orders = max(ORDER_COUNT_MIN, int(rng.poisson(ORDER_COUNT_POISSON_LAMBDA)))
        avg_invoice_value = revenue / max(number_of_orders, 1)
        product_count = int(rng.integers(1, 6))

        # Payment behavior
        payment_delay_days = max(PAYMENT_DELAY_MIN, rng.normal(PAYMENT_DELAY_MEAN, PAYMENT_DELAY_STD))
        overdue_amount = revenue * rng.uniform(OVERDUE_RATIO_MIN, OVERDUE_RATIO_MAX)

        # Credit and exposure
        credit_limit = revenue * rng.uniform(CREDIT_LIMIT_MIN_MULT, CREDIT_LIMIT_MAX_MULT)
        current_exposure = revenue * rng.uniform(EXPOSURE_AMOUNT_MIN_MULT, EXPOSURE_AMOUNT_MAX_MULT)

        # Tenure and default
        relationship_length_months = int(rng.integers(TENURE_MONTHS_MIN, TENURE_MONTHS_MAX + 1))
        default_flag = rng.random() < DEFAULT_PROBABILITY

        customers.append({
            "customer_id": f"CUST{i:03d}",
            "country": rng.choice(COUNTRIES),
            "industry": rng.choice(INDUSTRIES),
            "company_size": rng.choice(COMPANY_SIZES),
            "annual_revenue": round(revenue, 2),
            "gross_margin": round(margin, 4),
            "number_of_orders": number_of_orders,
            "invoice_count": number_of_orders,
            "avg_invoice_value": round(avg_invoice_value, 2),
            "product_count": product_count,
            "payment_delay_days": round(payment_delay_days, 1),
            "overdue_amount": round(overdue_amount, 2),
            "product_category": rng.choice(PRODUCT_CATEGORIES),
            "credit_limit": round(credit_limit, 2),
            "current_exposure": round(current_exposure, 2),
            "relationship_length_months": relationship_length_months,
            "default_flag": int(default_flag),
        })

    return pd.DataFrame(customers)


def main() -> None:
    """Generate and save customer master data to CSV."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating synthetic customer master data...")
    df = generate_customer_master()

    output_file = RAW_DIR / "customer_master.csv"
    df.to_csv(output_file, index=False)

    print(f"✓ Customer master data generated: {output_file}")
    print(f"  - {len(df)} customers")
    print(f"  - {df['country'].nunique()} countries")
    print(f"  - {df['industry'].nunique()} industries")
    print(f"  - Total synthetic revenue: €{df['annual_revenue'].sum():,.0f}")


if __name__ == "__main__":
    main()
