from csv import DictReader, DictWriter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "customers.csv"
OUTPUT = ROOT / "output" / "customer_segments.csv"


def score_customer(row):
    revenue = float(row["annual_revenue_eur"])
    months_active = int(row["months_active"])
    late_payments = int(row["late_payments"])
    balance = float(row["open_balance_eur"])

    value_score = 3 if revenue >= 600000 else 2 if revenue >= 300000 else 1
    activity_score = 3 if months_active >= 36 else 2 if months_active >= 12 else 1
    risk_score = late_payments * 15 + (balance / max(revenue, 1)) * 100

    if value_score >= 3 and risk_score < 20:
        segment = "High value / low risk"
    elif risk_score >= 45:
        segment = "Watchlist"
    elif activity_score <= 1:
        segment = "New relationship"
    else:
        segment = "Core customer"

    return {
        **row,
        "value_score": value_score,
        "activity_score": activity_score,
        "risk_score": round(risk_score, 1),
        "segment": segment,
    }


def main():
    with INPUT.open(newline="") as file:
        rows = [score_customer(row) for row in DictReader(file)]

    OUTPUT.parent.mkdir(exist_ok=True)
    with OUTPUT.open("w", newline="") as file:
        writer = DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()

