# Technical Notes — Customer Segmentation & Risk Evaluation

## Data generation assumptions
- The dataset is fully synthetic and designed as a portfolio demonstration.
- Customer records are generated with deterministic randomness using a fixed seed.
- Revenue is sampled from a normal distribution to reflect mid-market B2B accounts.
- Gross margin is constrained between typical commercial B2B boundaries.
- Payment delays, overdue amounts, and credit exposure are synthesized to support risk analysis.
- Customer tenure, order count, and product category diversity create realistic customer profiles.

## Feature engineering logic
- **overdue_ratio** = overdue_amount / annual_revenue, capped to prevent extreme outliers.
- **payment_delay_category** defined by business-friendly buckets: On Time, Moderate Delay, Delayed, High Delay.
- **revenue_per_order** and **gross_profit** provide profitability context.
- **exposure_utilization** = current_exposure / credit_limit, capped at 200%.
- **exposure_at_risk** = current_exposure + overdue_amount.
- **relationship_years** and **order_frequency** capture relationship maturity.
- **high_payment_delay_concentration** is a portfolio-level signal for payment risk.

## Segmentation logic
- Customers are clustered with KMeans on standardized inputs:
  - annual revenue
  - overdue ratio
  - payment delay days
  - gross margin
  - exposure utilization
- Cluster centers are interpreted with business rules to assign readable segment labels.
- Segment definitions are designed to support portfolio strategy and action planning.
- Labels include:
  - Strategic High-Value
  - Stable Low-Risk
  - Growth Potential
  - Late-Paying Watchlist
  - High-Risk Low-Margin

### Segment output fields
- `segment_id`: numeric cluster identifier
- `segment_name`: business-readable segment label
- `segment_description`: business interpretation
- `segment_priority`: action priority for portfolio managers
- `main_risk_driver`: primary risk theme per segment
- `commercial_action`: recommended next step

## Risk scoring formula
- **overdue_ratio** weight: 8.0
- **payment_delay_days** weight: 0.033 per day
- **margin_quality** weight: 2.5 (margin below 20% increases risk)
- **default_flag** weight: 15.0
- **exposure_utilization** weight: 2.0
- **relationship_years** weight: -0.1 (longer relationships slightly reduce risk)

### Risk categories
- Low Risk: score < 2.5
- Medium Risk: 2.5 ≤ score < 5.0
- Elevated Risk: 5.0 ≤ score < 8.0
- High Risk: score ≥ 8.0

### Risk output fields
- `risk_score`
- `risk_category`
- `risk_band`
- `default_probability_proxy`
- `exposure_at_risk`
- `payment_behavior_score`
- `profitability_score`
- `commercial_value_score`

## SQL analytics layer
- `sql/customer_segmentation_queries.sql` provides 10 realistic business analytics queries.
- Uses CTEs, CASE expressions, aggregations, and window-friendly logic.
- Queries support common business views such as portfolio overview, segment revenue, risk distribution, overdue country analysis, and exposure bands.

## Power BI dataset design
- Output is a flat table optimized for BI dashboards.
- Column names are cleaned and made business-friendly.
- Includes summary dimensions for segment, risk, geography, and finance.
- Designed for dashboard pages: executive overview, segment analysis, risk evaluation, revenue & margin, and customer drilldown.

## Testing approach
- `tests/test_pipeline.py` validates the end-to-end pipeline run and output file creation.
- Checks include:
  - output existence
  - required column presence
  - unique customer IDs
  - valid risk categories
  - risk score range
- `tests/test_sample_data.py` ensures the sample data file remains available.

## Known limitations
- Synthetic data only; not representative of any single real company.
- Risk framework is illustrative, not a production credit model.
- No time-series or cohort analysis in the current version.
- Segment labels are derived from clustering heuristics and should be validated with business stakeholders.

## Future extensions
- Integrate historical transaction and cohort analysis.
- Add scenario-based portfolio stress testing.
- Support live BI refresh from a data warehouse or database.
- Add structured rule-based credit policy thresholds for automated alerts.
- Implement cluster explainability and segment stability validation.
