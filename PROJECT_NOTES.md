# Project Notes — Customer Segmentation & Risk Evaluation

## Business problem
Segment customers and assess risk across a portfolio to enable targeted retention and risk-adjusted decision making.

## What I built
- Customer feature engineering and segmentation pipeline in `src/feature_engineering.py` and `src/segmentation_model.py`.
- Risk scoring logic in `src/risk_scoring.py`.
- Power BI-ready outputs and sample data for dashboarding.
- Streamlit demo at `src/app.py` for interactive exploration.

## Key technical points
- Built a reproducible ML workflow with scikit-learn clustering.
- Emphasised explainability and segment-level KPI outputs.
- Added Docker, CI, smoke testing, and project note documentation.
- Included sample dataset and unit tests for maintainability.

## Project story
1. Challenge: identify meaningful customer segments and quantify risk across them.
2. Solution: engineer features, build clusters, score risk, and expose outputs for reporting.
3. Impact: helps portfolio managers optimise retention strategies and identify risk concentrations.
4. Tradeoffs: synthetic data allows focus on model design while avoiding real customer data.

## Lessons and improvements
- Next step: add cluster explainability with SHAP and tuning for cluster stability.
- Key points: feature choices, model metrics, and how clustering supports business decisions.
