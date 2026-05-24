"""
Main pipeline orchestrator for customer segmentation and risk evaluation.

This script runs the complete analytical pipeline:
1. Generate synthetic customer data
2. Engineer customer features
3. Segment customers into business-relevant groups
4. Compute risk scores
5. Export BI-ready dataset

Outputs are saved to data/processed and data/powerbi directories.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_customer_data import main as generate_data
from feature_engineering import main as engineer_features
from segmentation_model import main as segment_customers
from risk_scoring import main as score_risks
from export_powerbi import main as export_powerbi


def main():
    """Run the complete customer segmentation pipeline."""
    print("=" * 80)
    print("CUSTOMER SEGMENTATION & RISK EVALUATION PIPELINE")
    print("=" * 80)
    print()

    try:
        print("STEP 1: Generating synthetic customer data...")
        print("-" * 80)
        generate_data()
        print()

        print("STEP 2: Engineering customer features...")
        print("-" * 80)
        engineer_features()
        print()

        print("STEP 3: Segmenting customers...")
        print("-" * 80)
        segment_customers()
        print()

        print("STEP 4: Computing risk scores...")
        print("-" * 80)
        score_risks()
        print()

        print("STEP 5: Exporting BI-ready dataset...")
        print("-" * 80)
        export_powerbi()
        print()

        print("=" * 80)
        print("✓ PIPELINE COMPLETE")
        print("=" * 80)
        print("Outputs available in:")
        print("  - data/raw/: Raw customer master data")
        print("  - data/processed/: Engineered features, segments, risk scores")
        print("  - data/powerbi/: BI-ready export for dashboarding")
        print()
        print("Wrote customer segmentation outputs to data/ directory")

    except Exception as e:
        print(f"\n✗ Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()
