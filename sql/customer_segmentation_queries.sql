-- Customer segmentation and risk evaluation queries

SELECT COUNT(*) AS total_customers,
       SUM(revenue) AS total_revenue,
       AVG(margin) AS avg_margin
FROM customer_features;

SELECT segment_label,
       COUNT(*) AS customer_count,
       SUM(revenue) AS revenue,
       AVG(risk_score) AS avg_risk_score,
       AVG(payment_delay) AS avg_payment_delay
FROM customer_segments
JOIN risk_scored_customers USING (customer_id)
GROUP BY segment_label;

SELECT country,
       SUM(overdue_amount) AS total_overdue,
       SUM(revenue) AS total_revenue
FROM customer_features
GROUP BY country
ORDER BY total_overdue DESC;
