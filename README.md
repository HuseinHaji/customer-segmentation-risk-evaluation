# Customer Segmentation & Risk Evaluation

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![SQL](https://img.shields.io/badge/SQL-PostgreSQL%20style-blueviolet)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-orange)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Reproducible-blue)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-pytest-brightgreen)](https://pytest.org/)
[![Synthetic Data](https://img.shields.io/badge/Data-Synthetic-gray)](#)

## Project summary

Customer Segmentation & Risk Evaluation is a synthetic B2B analytics project that demonstrates how customer-level revenue, margin, payment behavior, and exposure data can be transformed into business-readable segments, risk categories, and BI-ready reporting outputs.

This portfolio case study is designed to demonstrate analytics thinking for roles in data analysis, BI, credit risk, and portfolio management.

## Business context

A business wants to understand how its B2B customer portfolio behaves across value, payment performance, profitability, and exposure. The goal is to produce management-ready insights that support customer relationship planning, risk-adjusted decisions, and portfolio monitoring.

## Business questions

- Which customer segments deliver the most revenue and margin?
- Where is payment exposure concentrated by country, industry, and customer segment?
- Which customers should be prioritized for credit review or relationship management?
- How can risk-adjusted commercial actions support portfolio stability?

## Architecture

This repo contains a deterministic pipeline from synthetic raw data to analytics-ready outputs:

1. Data generation: `src/generate_customer_data.py`
2. Feature engineering: `src/feature_engineering.py`
3. Customer segmentation: `src/segmentation_model.py`
4. Risk scoring: `src/risk_scoring.py`
5. Power BI export: `src/export_powerbi.py`
6. Interactive dashboard: `src/app.py`

## Dataset and outputs

The pipeline produces the following datasets:

- `data/processed/customer_features.csv`
- `data/processed/customer_segments.csv`
- `data/processed/risk_scored_customers.csv`
- `data/processed/segment_summary.csv`
- `data/powerbi/powerbi_customer_dashboard.csv`

These outputs are designed for BI reporting, executive review, and dashboard consumption.

## Methodology

### Feature engineering
- Payment performance: payment delay, overdue ratio, payment delay category
- Profitability: gross margin, revenue per order, gross profit
- Credit exposure: exposure utilization, current exposure, exposure at risk
- Relationship health: tenure, order frequency
- Risk indicators: default history, overdue concentration

### Segmentation
Customers are segmented with KMeans clustering and business-labeled into practical categories:
- Strategic High-Value Customers
- Stable Low-Risk Customers
- Growth Potential Customers
- Late-Paying Watchlist
- High-Risk Low-Margin Customers
- New / Limited-History Customers

### Risk scoring
A transparent composite score is calculated using:
- overdue ratio
- payment delay
- exposure utilization
- default history
- margin quality
- relationship length

Risk categories:
- Low Risk
- Medium Risk
- Elevated Risk
- High Risk

## Key KPIs

- Total portfolio revenue
- Average gross margin
- High-risk customer share
- Average payment delay
- Exposure at risk
- Overdue amount
- Segment revenue and margin
- Risk category distribution
- Default proxy rate

## Outputs

| Output | Purpose |
|---|---|
| `data/processed/customer_features.csv` | Customer-level engineered attributes: revenue, margin, invoice count, product count, payment behavior, exposure utilization, risk score, risk category, and segment label. |
| `data/processed/customer_segments.csv` | Customer-level segmentation output with segment description, priority, main risk driver, and commercial action. |
| `data/processed/risk_scored_customers.csv` | Explainable risk scoring table with risk band, default probability proxy, exposure at risk, overdue ratio, payment behavior score, profitability score, and commercial value score. |
| `data/processed/segment_summary.csv` | Segment-level management summary with revenue, exposure, margin, payment delay, overdue amount, high-risk share, default proxy rate, and recommended action. |
| `data/powerbi/powerbi_customer_dashboard.csv` | Flat BI-ready output for Power BI, Tableau, or Streamlit dashboarding. |

## Dashboard design

The Streamlit demo and Power BI-ready export are designed around five management reporting pages:

| Page | Dashboard content |
|---|---|
| Executive Overview | Total customers, total revenue, total exposure, high-risk customer share, average margin, segment distribution, and risk category distribution. |
| Segment Analysis | Customers by segment, revenue by segment, margin by segment, segment recommendations, and segment comparison table. |
| Risk Evaluation | Risk category distribution, exposure at risk, overdue amount by country, high-risk customers by industry, and payment delay analysis. |
| Revenue & Margin | Revenue by segment, margin by industry, customer value versus risk, and profitability score distribution. |
| Customer Drilldown | Customer-level table, segment filter, risk category filter, country/industry filter, and customer profile view. |

The app also includes a methodology and data-quality section explaining that the pipeline uses a synthetic portfolio dataset and an illustrative scoring framework.

## How to run

```bash
cd customer-segmentation-risk-evaluation
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/segment_customers.py
streamlit run src/app.py
```

For Docker:

```bash
docker-compose up --build
```

## Repository structure

```text
customer-segmentation-risk-evaluation/
├── README.md
├── PROJECT_SUMMARY.md
├── PROJECT_NOTES.md
├── PORTFOLIO_COPY.md
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── powerbi/
│   └── sample/
├── sql/
│   └── customer_segmentation_queries.sql
├── src/
│   ├── config.py
│   ├── generate_customer_data.py
│   ├── feature_engineering.py
│   ├── segmentation_model.py
│   ├── risk_scoring.py
│   ├── export_powerbi.py
│   ├── app.py
│   └── segment_customers.py
├── tests/
│   ├── test_pipeline.py
│   └── test_sample_data.py
└── screenshots/
    └── README.md
```

## Example insights

- Strategic High-Value customers contribute a large share of portfolio revenue while maintaining strong payment performance.
- Late-Paying Watchlist customers have acceptable revenue but elevated overdue amounts and payment delay risks.
- High-Risk Low-Margin customers are candidates for exposure reduction, pricing review, or portfolio exit.

## Skills demonstrated

| Skill | Where demonstrated |
|---|---|
| Python | Synthetic data generation, feature engineering, pipeline orchestration |
| pandas | Data transformation, aggregation, validation |
| numpy | Probabilistic synthetic data generation |
| scikit-learn | Clustering for customer segmentation |
| SQL | Analytical queries for portfolio review |
| Power BI-ready modeling | BI export, dashboard-ready dataset preparation |
| Streamlit | Interactive portfolio dashboard |
| Docker | Containerized reproducible environment |
| CI/CD | GitHub Actions workflow, pytest coverage |
| Testing | Pipeline output and data validation tests |
| Business analytics | Segment interpretation, KPI synthesis |
| Risk analytics | Explainable risk score, exposure analysis |

## Limitations

- Uses fully synthetic portfolio data and illustrative scoring logic.
- Not a regulated credit model; risk scores are for demonstration only.
- Segmentation is based on a single static snapshot without time-series data.
- Reported insights are simulated business case observations, not measured real-world business impact.

## Future improvements

- Add time-series cohort analysis and rolling risk monitoring.
- Integrate a BI dashboard source file for Power BI or Tableau.
- Expand the dataset with customer engagement and product usage metrics.
- Add business rule validation for credit policy thresholds.

## Repository notes

Suggested GitHub repository topics:
`data-analytics`, `customer-segmentation`, `risk-scoring`, `business-intelligence`, `python`, `sql`, `streamlit`, `powerbi`, `portfolio-project`, `synthetic-data`

Suggested GitHub About description:
"Synthetic B2B customer segmentation and risk evaluation project using Python, SQL, Streamlit, and Power BI-ready outputs."

## Disclaimer

This project uses a synthetic portfolio dataset created for portfolio demonstration. It does not contain real company data, proprietary information, or actual customer records. The risk scoring framework is designed to demonstrate transparent credit/risk analytics logic and should not be interpreted as a regulated credit model.
