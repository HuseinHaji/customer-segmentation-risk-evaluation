from csv import DictReader, DictWriter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "customers.csv"
OUTPUT_DIR = ROOT / "output"
REQUIRED_FIELDS = [
    "customer_id",
    "sector",
    "annual_revenue_eur",
    "months_active",
    "late_payments",
    "open_balance_eur",
]


def as_float(row, field):
    try:
        return float(row[field])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{row.get('customer_id', 'unknown')}: invalid {field}") from exc


def score_customer(row):
    revenue = as_float(row, "annual_revenue_eur")
    months_active = int(row["months_active"])
    late_payments = int(row["late_payments"])
    balance = as_float(row, "open_balance_eur")

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

    exposure_pct = balance / max(revenue, 1)
    next_best_action = {
        "High value / low risk": "Protect relationship; offer premium analytics review",
        "Watchlist": "Run payment-risk review and agree remediation plan",
        "New relationship": "Build onboarding cadence and baseline behavior",
        "Core customer": "Monitor activity and cross-sell relevant service",
    }[segment]

    return {
        **row,
        "value_score": value_score,
        "activity_score": activity_score,
        "risk_score": round(risk_score, 1),
        "open_balance_to_revenue": round(exposure_pct, 3),
        "segment": segment,
        "next_best_action": next_best_action,
    }


def build_segment_summary(rows):
    grouped = {}
    for row in rows:
        bucket = grouped.setdefault(
            row["segment"],
            {"segment": row["segment"], "customers": 0, "revenue": 0.0, "balance": 0.0, "risk_score": 0.0},
        )
        bucket["customers"] += 1
        bucket["revenue"] += as_float(row, "annual_revenue_eur")
        bucket["balance"] += as_float(row, "open_balance_eur")
        bucket["risk_score"] += row["risk_score"]

    summary = []
    for values in grouped.values():
        summary.append(
            {
                "segment": values["segment"],
                "customers": values["customers"],
                "annual_revenue_eur": round(values["revenue"], 2),
                "open_balance_eur": round(values["balance"], 2),
                "avg_risk_score": round(values["risk_score"] / values["customers"], 1),
                "balance_to_revenue": round(values["balance"] / values["revenue"], 3),
            }
        )
    return sorted(summary, key=lambda item: item["annual_revenue_eur"], reverse=True)


def build_action_queue(rows):
    priority = {"Watchlist": 1, "High value / low risk": 2, "New relationship": 3, "Core customer": 4}
    queue = []
    for row in rows:
        if row["segment"] in {"Watchlist", "High value / low risk", "New relationship"}:
            queue.append(
                {
                    "customer_id": row["customer_id"],
                    "sector": row["sector"],
                    "segment": row["segment"],
                    "risk_score": row["risk_score"],
                    "annual_revenue_eur": row["annual_revenue_eur"],
                    "next_best_action": row["next_best_action"],
                }
            )
    return sorted(queue, key=lambda item: (priority[item["segment"]], -float(item["annual_revenue_eur"])))


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="") as file:
        writer = DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main():
    with INPUT.open(newline="") as file:
        input_rows = list(DictReader(file))
    missing = [field for field in REQUIRED_FIELDS if input_rows and field not in input_rows[0]]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    rows = [score_customer(row) for row in input_rows]

    OUTPUT_DIR.mkdir(exist_ok=True)
    write_csv(OUTPUT_DIR / "customer_segments.csv", rows)
    write_csv(OUTPUT_DIR / "segment_summary.csv", build_segment_summary(rows))
    write_csv(OUTPUT_DIR / "action_queue.csv", build_action_queue(rows))

    print(f"Wrote customer segmentation outputs to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
