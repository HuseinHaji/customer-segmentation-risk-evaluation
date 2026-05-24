-- ============================================================================
-- CUSTOMER SEGMENTATION & RISK EVALUATION SQL ANALYTICS
-- ============================================================================
--
-- This SQL module provides a comprehensive analytics layer for customer
-- segmentation and risk evaluation. Queries are designed to:
-- 1. Demonstrate SQL proficiency (CTEs, window functions, aggregations)
-- 2. Support business decision-making with clear, actionable metrics
-- 3. Be compatible with PostgreSQL and modern SQL dialects
-- 4. Use best practices: comments, formatting, readable logic
--
-- Note: These queries are designed to work with the processed data model
-- output from the Python pipeline (customer_features, customer_segments, etc.)
-- In practice, these would join against actual database tables.
--
-- ============================================================================


-- ============================================================================
-- QUERY 1: CUSTOMER PORTFOLIO OVERVIEW
-- ============================================================================
-- Returns high-level portfolio metrics across all customers
-- KPIs: Total customers, revenue, exposure, margin, risk distribution

SELECT
    COUNT(DISTINCT customer_id) as total_customers,
    SUM(annual_revenue) as total_revenue,
    ROUND(AVG(annual_revenue), 2) as avg_revenue,
    ROUND(AVG(gross_margin), 4) as avg_gross_margin,
    SUM(current_exposure) as total_exposure,
    ROUND(AVG(exposure_utilization), 4) as avg_exposure_utilization,
    SUM(overdue_amount) as total_overdue_amount,
    ROUND(AVG(risk_score), 2) as avg_risk_score,
    MIN(risk_score) as min_risk_score,
    MAX(risk_score) as max_risk_score,
    ROUND(AVG(payment_delay_days), 1) as avg_payment_delay_days,
    SUM(CASE WHEN default_flag = 1 THEN 1 ELSE 0 END) as customers_with_default_history
FROM customer_features
WHERE annual_revenue > 0;


-- ============================================================================
-- QUERY 2: SEGMENT-LEVEL REVENUE AND PROFITABILITY ANALYSIS
-- ============================================================================
-- Analyzes revenue, margin, and profitability by customer segment
-- Useful for: Revenue planning, segment contribution analysis, margin optimization

WITH segment_metrics AS (
    SELECT
        cs.segment_name,
        cs.segment_description,
        COUNT(DISTINCT cs.customer_id) as num_customers,
        SUM(cf.annual_revenue) as total_segment_revenue,
        ROUND(AVG(cf.annual_revenue), 2) as avg_customer_revenue,
        ROUND(AVG(cf.gross_margin), 4) as avg_margin,
        SUM(cf.annual_revenue * cf.gross_margin) as total_gross_profit,
        ROUND(SUM(cf.annual_revenue * cf.gross_margin) / NULLIF(SUM(cf.annual_revenue), 0), 4) as blended_margin,
        SUM(cf.current_exposure) as total_exposure,
        SUM(cf.overdue_amount) as total_overdue,
        ROUND(AVG(cf.exposure_utilization), 4) as avg_utilization
    FROM customer_segments cs
    JOIN customer_features cf ON cs.customer_id = cf.customer_id
    GROUP BY cs.segment_name, cs.segment_description
)
SELECT
    segment_name,
    segment_description,
    num_customers,
    total_segment_revenue as revenue,
    avg_customer_revenue,
    avg_margin,
    total_gross_profit as gross_profit,
    blended_margin,
    total_exposure,
    total_overdue,
    avg_utilization,
    ROUND(100.0 * total_segment_revenue / (SELECT SUM(annual_revenue) FROM customer_features), 2) as pct_total_revenue
FROM segment_metrics
ORDER BY total_segment_revenue DESC;


-- ============================================================================
-- QUERY 3: RISK CATEGORY DISTRIBUTION AND EXPOSURE ANALYSIS
-- ============================================================================
-- Summarizes risk profile across portfolio with exposure concentration
-- Useful for: Risk reporting, exposure limits monitoring, capital allocation

WITH risk_summary AS (
    SELECT
        rc.risk_category,
        COUNT(DISTINCT rc.customer_id) as num_customers,
        ROUND(AVG(rc.risk_score), 2) as avg_risk_score,
        SUM(cf.annual_revenue) as total_revenue,
        SUM(cf.current_exposure) as total_exposure,
        SUM(cf.overdue_amount) as total_overdue,
        ROUND(AVG(cf.gross_margin), 4) as avg_margin,
        ROUND(AVG(cf.payment_delay_days), 1) as avg_payment_delay,
        SUM(CASE WHEN cf.default_flag = 1 THEN 1 ELSE 0 END) as customers_with_default
    FROM risk_scored_customers rc
    JOIN customer_features cf ON rc.customer_id = cf.customer_id
    GROUP BY rc.risk_category
)
SELECT
    risk_category,
    num_customers,
    ROUND(100.0 * num_customers / (SELECT COUNT(*) FROM customer_features), 2) as pct_of_portfolio,
    total_revenue,
    ROUND(100.0 * total_revenue / (SELECT SUM(annual_revenue) FROM customer_features), 2) as pct_of_revenue,
    total_exposure,
    total_overdue,
    avg_margin,
    avg_payment_delay,
    avg_risk_score,
    customers_with_default,
    ROUND(100.0 * customers_with_default / NULLIF(num_customers, 0), 2) as default_rate_pct
FROM risk_summary
ORDER BY CASE
    WHEN risk_category = 'Low Risk' THEN 1
    WHEN risk_category = 'Medium Risk' THEN 2
    WHEN risk_category = 'Elevated Risk' THEN 3
    WHEN risk_category = 'High Risk' THEN 4
END;


-- ============================================================================
-- QUERY 4: HIGH-RISK EXPOSURE BY INDUSTRY
-- ============================================================================
-- Identifies industry-level risk concentrations and exposure hot spots
-- Useful for: Industry strategy, portfolio rebalancing, risk appetite monitoring

SELECT
    cf.industry,
    COUNT(DISTINCT cf.customer_id) as num_customers,
    COUNT(DISTINCT CASE WHEN rc.risk_category IN ('Elevated Risk', 'High Risk') THEN cf.customer_id END) as high_risk_customers,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN rc.risk_category IN ('Elevated Risk', 'High Risk') THEN cf.customer_id END)
        / COUNT(DISTINCT cf.customer_id), 2) as pct_high_risk,
    SUM(cf.current_exposure) as total_exposure,
    SUM(CASE WHEN rc.risk_category IN ('Elevated Risk', 'High Risk') THEN cf.current_exposure ELSE 0 END) as high_risk_exposure,
    ROUND(AVG(rc.risk_score), 2) as avg_risk_score,
    SUM(cf.overdue_amount) as total_overdue,
    ROUND(AVG(cf.gross_margin), 4) as avg_margin
FROM customer_features cf
LEFT JOIN risk_scored_customers rc ON cf.customer_id = rc.customer_id
GROUP BY cf.industry
ORDER BY high_risk_exposure DESC;


-- ============================================================================
-- QUERY 5: OVERDUE AMOUNT AND PAYMENT BEHAVIOR BY COUNTRY
-- ============================================================================
-- Geographic analysis of payment behavior and collection risk
-- Useful for: Regional collections strategy, working capital management

SELECT
    cf.country,
    COUNT(DISTINCT cf.customer_id) as num_customers,
    SUM(cf.annual_revenue) as total_revenue,
    SUM(cf.overdue_amount) as total_overdue,
    ROUND(100.0 * SUM(cf.overdue_amount) / NULLIF(SUM(cf.annual_revenue), 0), 2) as overdue_ratio_pct,
    ROUND(AVG(cf.payment_delay_days), 1) as avg_payment_delay_days,
    COUNT(DISTINCT CASE WHEN cf.payment_delay_days > 30 THEN cf.customer_id END) as customers_with_high_delay,
    ROUND(AVG(rc.risk_score), 2) as avg_risk_score,
    ROUND(AVG(cf.gross_margin), 4) as avg_margin
FROM customer_features cf
LEFT JOIN risk_scored_customers rc ON cf.customer_id = rc.customer_id
GROUP BY cf.country
ORDER BY total_overdue DESC;


-- ============================================================================
-- QUERY 6: TOP 20 CUSTOMERS BY EXPOSURE AT RISK
-- ============================================================================
-- Identifies key customers with highest risk-adjusted exposure
-- Useful for: Portfolio concentration analysis, relationship management priorities

SELECT
    rc.customer_id,
    cf.country,
    cf.industry,
    cf.annual_revenue,
    cf.gross_margin,
    cs.segment_name,
    rc.risk_category,
    ROUND(rc.risk_score, 2) as risk_score,
    cf.current_exposure,
    cf.overdue_amount,
    (cf.current_exposure + cf.overdue_amount) as exposure_at_risk,
    ROUND(cf.exposure_utilization, 4) as exposure_utilization,
    cf.payment_delay_days,
    cf.relationship_length_months
FROM risk_scored_customers rc
JOIN customer_features cf ON rc.customer_id = cf.customer_id
JOIN customer_segments cs ON rc.customer_id = cs.customer_id
ORDER BY (cf.current_exposure + cf.overdue_amount) DESC
LIMIT 20;


-- ============================================================================
-- QUERY 7: SEGMENT-LEVEL DEFAULT PROXY RATE AND RISK METRICS
-- ============================================================================
-- Segment-level risk aggregation for credit policy monitoring
-- Useful for: Segment risk appetite, credit policy calibration

WITH segment_risk AS (
    SELECT
        cs.segment_name,
        COUNT(DISTINCT cs.customer_id) as num_customers,
        SUM(CASE WHEN cf.default_flag = 1 THEN 1 ELSE 0 END) as customers_with_default,
        ROUND(AVG(cf.default_flag), 4) as default_rate,
        ROUND(AVG(rc.risk_score), 2) as avg_risk_score,
        COUNT(DISTINCT CASE WHEN rc.risk_category IN ('Elevated Risk', 'High Risk') THEN cs.customer_id END) as high_risk_count,
        ROUND(AVG(CASE WHEN rc.risk_category IN ('Elevated Risk', 'High Risk') THEN 1 ELSE 0 END), 4) as high_risk_rate,
        SUM(cf.current_exposure) as total_exposure,
        SUM(cf.overdue_amount) as total_overdue,
        ROUND(AVG(cf.exposure_utilization), 4) as avg_utilization
    FROM customer_segments cs
    JOIN customer_features cf ON cs.customer_id = cf.customer_id
    LEFT JOIN risk_scored_customers rc ON cs.customer_id = rc.customer_id
    GROUP BY cs.segment_name
)
SELECT
    segment_name,
    num_customers,
    customers_with_default,
    ROUND(100.0 * default_rate, 2) as default_rate_pct,
    avg_risk_score,
    high_risk_count,
    ROUND(100.0 * high_risk_rate, 2) as high_risk_pct,
    total_exposure,
    total_overdue,
    avg_utilization
FROM segment_risk
ORDER BY default_rate DESC;


-- ============================================================================
-- QUERY 8: PAYMENT DELAY DISTRIBUTION AND CONCENTRATION
-- ============================================================================
-- Analyzes payment delay patterns across portfolio for collections insight
-- Useful for: DSO analysis, working capital forecasting

WITH delay_buckets AS (
    SELECT
        CASE
            WHEN cf.payment_delay_days <= 7 THEN '0-7 days (On Time)'
            WHEN cf.payment_delay_days <= 14 THEN '8-14 days (Moderate)'
            WHEN cf.payment_delay_days <= 30 THEN '15-30 days (Delayed)'
            ELSE '>30 days (High Delay)'
        END as delay_category,
        COUNT(DISTINCT cf.customer_id) as num_customers,
        SUM(cf.annual_revenue) as total_revenue,
        SUM(cf.overdue_amount) as total_overdue,
        ROUND(AVG(rc.risk_score), 2) as avg_risk_score,
        ROUND(AVG(cf.payment_delay_days), 1) as avg_payment_days
    FROM customer_features cf
    LEFT JOIN risk_scored_customers rc ON cf.customer_id = rc.customer_id
    GROUP BY delay_category
)
SELECT
    delay_category,
    num_customers,
    ROUND(100.0 * num_customers / (SELECT COUNT(*) FROM customer_features), 2) as pct_customers,
    total_revenue,
    ROUND(100.0 * total_revenue / (SELECT SUM(annual_revenue) FROM customer_features), 2) as pct_revenue,
    total_overdue,
    avg_risk_score,
    avg_payment_days
FROM delay_buckets
ORDER BY CASE
    WHEN delay_category = '0-7 days (On Time)' THEN 1
    WHEN delay_category = '8-14 days (Moderate)' THEN 2
    WHEN delay_category = '15-30 days (Delayed)' THEN 3
    ELSE 4
END;


-- ============================================================================
-- QUERY 9: EXPOSURE UTILIZATION BAND ANALYSIS
-- ============================================================================
-- Categorizes customers by credit utilization for credit management
-- Useful for: Credit limit review, concentration management

WITH utilization_bands AS (
    SELECT
        CASE
            WHEN cf.exposure_utilization <= 0.33 THEN 'Low (0-33%)'
            WHEN cf.exposure_utilization <= 0.67 THEN 'Moderate (34-67%)'
            WHEN cf.exposure_utilization <= 1.0 THEN 'High (68-100%)'
            ELSE 'Over-Utilized (>100%)'
        END as utilization_band,
        COUNT(DISTINCT cf.customer_id) as num_customers,
        SUM(cf.annual_revenue) as total_revenue,
        SUM(cf.current_exposure) as total_exposure,
        SUM(cf.credit_limit) as total_credit_limit,
        ROUND(AVG(cf.exposure_utilization), 4) as avg_utilization,
        ROUND(AVG(rc.risk_score), 2) as avg_risk_score,
        ROUND(AVG(cf.gross_margin), 4) as avg_margin
    FROM customer_features cf
    LEFT JOIN risk_scored_customers rc ON cf.customer_id = rc.customer_id
    GROUP BY utilization_band
)
SELECT
    utilization_band,
    num_customers,
    ROUND(100.0 * num_customers / (SELECT COUNT(*) FROM customer_features), 2) as pct_customers,
    total_revenue,
    total_exposure,
    total_credit_limit,
    ROUND(100.0 * total_exposure / NULLIF(total_credit_limit, 0), 2) as actual_utilization_pct,
    avg_utilization,
    avg_risk_score,
    avg_margin
FROM utilization_bands
ORDER BY CASE
    WHEN utilization_band = 'Low (0-33%)' THEN 1
    WHEN utilization_band = 'Moderate (34-67%)' THEN 2
    WHEN utilization_band = 'High (68-100%)' THEN 3
    ELSE 4
END;


-- ============================================================================
-- QUERY 10: BI DASHBOARD BASE TABLE
-- ============================================================================
-- Complete denormalized view ready for Power BI or Tableau
-- Combines all dimensions (segment, risk, geography, product) for dashboard

SELECT
    cf.customer_id,
    cf.country,
    cf.industry,
    cf.company_size,
    cf.annual_revenue,
    cf.gross_margin,
    cf.gross_profit,
    cf.number_of_orders,
    cf.avg_invoice_value,
    cf.payment_delay_days,
    cf.payment_delay_category,
    cf.overdue_amount,
    cf.overdue_ratio,
    cf.product_category,
    cf.credit_limit,
    cf.current_exposure,
    cf.exposure_utilization,
    (cf.current_exposure + cf.overdue_amount) as exposure_at_risk,
    cf.relationship_length_months,
    cf.relationship_length_months / 12.0 as relationship_years,
    cf.default_flag,
    cs.segment_name,
    cs.segment_description,
    cs.segment_priority,
    rc.risk_score,
    rc.risk_category,
    rc.risk_band,
    rc.default_probability_proxy,
    rc.payment_behavior_score,
    rc.profitability_score,
    rc.commercial_value_score,
    CURRENT_DATE as snapshot_date
FROM customer_features cf
LEFT JOIN customer_segments cs ON cf.customer_id = cs.customer_id
LEFT JOIN risk_scored_customers rc ON cf.customer_id = rc.customer_id
ORDER BY cf.annual_revenue DESC;
