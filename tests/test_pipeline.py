import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with path.open(newline="") as file:
        return list(csv.DictReader(file))


def test_pipeline_generates_processed_outputs():
    result = subprocess.run(
        [sys.executable, "src/segment_customers.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    output_text = result.stdout.lower()
    assert "pipeline complete" in output_text

    processed_files = [
        ROOT / "data" / "processed" / "customer_features.csv",
        ROOT / "data" / "processed" / "customer_segments.csv",
        ROOT / "data" / "processed" / "risk_scored_customers.csv",
        ROOT / "data" / "processed" / "segment_summary.csv",
        ROOT / "data" / "powerbi" / "powerbi_customer_dashboard.csv",
    ]

    for path in processed_files:
        assert path.exists(), f"Missing expected output file: {path}"

    customer_rows = read_csv(ROOT / "data" / "processed" / "customer_features.csv")
    risk_rows = read_csv(ROOT / "data" / "processed" / "risk_scored_customers.csv")

    assert customer_rows, "customer_features.csv should not be empty"
    assert risk_rows, "risk_scored_customers.csv should not be empty"

    customer_ids = {row["customer_id"] for row in customer_rows}
    assert len(customer_ids) == len(customer_rows), "Duplicate customer_id found in customer_features.csv"

    assert all(row["segment_name"] for row in customer_rows), "All customers must have a segment_name"
    assert all(row["risk_category"] in {"Low Risk", "Medium Risk", "Elevated Risk", "High Risk"} for row in risk_rows)

    # Ensure risk scores are numeric and in a realistic range
    for row in risk_rows:
        score = float(row["risk_score"])
        assert 0 <= score <= 30

    assert any(row["risk_category"] == "High Risk" for row in risk_rows), "At least one High Risk customer expected"
