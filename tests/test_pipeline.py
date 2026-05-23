import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with path.open(newline="") as file:
        return list(csv.DictReader(file))


def test_pipeline_generates_customer_intelligence_outputs():
    result = subprocess.run(
        [sys.executable, "src/segment_customers.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "customer segmentation outputs" in result.stdout

    customers = read_csv(ROOT / "output" / "customer_segments.csv")
    segments = read_csv(ROOT / "output" / "segment_summary.csv")
    treatment = read_csv(ROOT / "output" / "treatment_plan.csv")
    sectors = read_csv(ROOT / "output" / "sector_summary.csv")

    assert len(customers) == 8
    assert {"Watchlist", "High value / low risk"} <= {row["segment"] for row in customers}
    assert all(row["risk_tier"] in {"low", "medium", "high"} for row in customers)
    assert treatment[0]["playbook"]
    assert sectors
    assert segments
