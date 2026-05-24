# Project Summary

## Problem
A synthetic B2B portfolio needs a structured analytics workflow to answer critical portfolio monitoring questions: how to segment customers by value, payment performance, profitability, and risk exposure, and how to convert those insights into BI-ready reporting.

## Solution
This project builds a reproducible analytics pipeline that:
- generates synthetic B2B customer master data,
- engineers business-relevant features for customer value and payment behavior,
- applies segmentation with explainable cluster labels,
- computes an illustrative risk score and category,
- exports a flat BI-ready dataset for dashboarding.

## Workflow
1. **Data generation** creates a synthetic customer portfolio with revenue, margin, payment delay, exposure, and tenure metrics.
2. **Feature engineering** transforms raw data into payment, profitability, credit exposure, and relationship health measures.
3. **Segmentation** identifies five business-readable customer groups using KMeans clustering.
4. **Risk scoring** calculates a composite risk score and assigns Low, Medium, Elevated, or High risk categories.
5. **Dashboard export** produces a flat dataset for Power BI, complete with segment labels and risk annotations.

## Business value
- Provides a management-ready view of customer portfolio risk and value.
- Supports customer relationship planning and credit review prioritization.
- Enables segment-level decisions for growth, retention, and exposure control.
- Demonstrates how analytics can turn raw customer data into operational insights.

## Technical skills demonstrated
- Python data engineering and pandas transformations
- Scikit-learn clustering for segmentation
- Explainable risk scoring and financial logic
- SQL analytics for portfolio reporting
- Streamlit dashboard design and BI-ready export preparation
- Docker and CI-enabled reproducible workflow
- Testing and data validation

## Final outputs
- `data/processed/customer_features.csv`
- `data/processed/customer_segments.csv`
- `data/processed/risk_scored_customers.csv`
- `data/processed/segment_summary.csv`
- `data/powerbi/powerbi_customer_dashboard.csv`
- `src/app.py` interactive dashboard
- `sql/customer_segmentation_queries.sql`

## Mapping to analyst work
This case study is relevant for roles in data analysis, business intelligence, credit risk, and analytics engineering. It mirrors real-world tasks such as customer portfolio review, risk-adjusted segmentation, reporting automation, and dashboard-ready dataset preparation.
