# Customer Segmentation & Risk Evaluation

## Business Context

This project explores customer behavior and risk using synthetic customer master and financial metrics. The business aims to identify customer segments, assess risk exposure, and support targeted portfolio management.

The analysis is intended for management reporting and customer relationship planning.

## Business Value

- Identifies strategic customer segments for cross-sell and retention.
- Quantifies risk characteristics by customer group.
- Supports risk-adjusted revenue forecasting.
- Produces segment-level metrics for business review.

## Tech Stack

- Python 3.10+ (pandas, numpy, scikit-learn)
- PostgreSQL-style SQL
- Power BI-ready CSV outputs
- Jupyter Notebook for analysis

## Dataset

The data is fully synthetic. It includes customer demographics, revenue and margin metrics, payment behavior, overdue amounts, product exposure and credit information.

## Data Model

- `customer_features.csv`: engineered customer-level attributes.
- `customer_segments.csv`: cluster-based segment assignment.
- `risk_scored_customers.csv`: risk score and category.
- `segment_summary.csv`: aggregated segment metrics.
- `powerbi_customer_dashboard.csv`: dataset ready for visualization.

## Key KPIs

- Total revenue
- Average margin
- High-risk customer share
- Average payment delay
- Overdue amount
- Number of customer segments
- Revenue by segment
- Margin by segment
- Risk score by segment
- Default rate by segment

## Project Structure

```text
customer-segmentation-risk-evaluation/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/
│   ├── processed/
│   └── powerbi/
├── sql/
│   └── customer_segmentation_queries.sql
├── src/
│   ├── generate_customer_data.py
│   ├── feature_engineering.py
│   ├── segmentation_model.py
│   ├── risk_scoring.py
│   └── export_powerbi.py
├── notebooks/
│   └── customer_segmentation_analysis.ipynb
└── screenshots/
    └── .gitkeep
```

## How to Run

```bash
cd customer-segmentation-risk-evaluation
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/generate_customer_data.py
python src/feature_engineering.py
python src/segmentation_model.py
python src/risk_scoring.py
python src/export_powerbi.py
```

For Windows:

```powershell
.venv\Scriptsctivate
```

## Dashboard Design

Power BI pages:

1. Customer Overview
2. Segment Analysis
3. Risk Evaluation
4. Revenue & Margin Trends
5. Customer Drilldown

## Example Insights

- A small group of high-value customers deliver the largest portion of revenue but also carry elevated risk indicators.
- Stable low-risk segments show strong payment behavior and low overdue exposure.
- Growth potential customers show above-average revenue with moderate payment delay.

## Future Improvements

- Add time-series customer cohort analysis.
- Include product-level penetration by segment.
- Automate segment adjustment based on new customer data.

## Disclaimer

This project uses fully synthetic data created for portfolio demonstration purposes. It does not contain confidential, proprietary, or real company data.
