import pandas as pd
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[1]
PROCESSED_PATH = BASE_PATH / 'data' / 'processed'


def compute_risk_score(df):
    score = (df['overdue_ratio'] * 8) + (df['payment_delay'] / 30) + (1 - df['margin']) * 4
    return score


def assign_risk_category(score):
    if score < 2.5:
        return 'Low Risk'
    if score < 4.5:
        return 'Moderate Risk'
    return 'High Risk'


def main():
    customers = pd.read_csv(PROCESSED_PATH / 'customer_segments.csv')
    customers['risk_score'] = compute_risk_score(customers)
    customers['risk_category'] = customers['risk_score'].apply(assign_risk_category)
    customers['default_rate'] = customers['default_flag'].astype(int) * 1.0
    risk_df = customers[['customer_id', 'risk_score', 'risk_category', 'default_rate', 'cluster_label', 'country', 'industry', 'revenue', 'margin', 'payment_delay', 'overdue_amount']]
    risk_df.to_csv(PROCESSED_PATH / 'risk_scored_customers.csv', index=False)
    segment_summary = customers.groupby('cluster_label', as_index=False).agg(
        customer_count=('customer_id', 'count'),
        total_revenue=('revenue', 'sum'),
        avg_margin=('margin', 'mean'),
        avg_risk_score=('risk_score', 'mean'),
        default_rate=('default_flag', 'mean')
    ).rename(columns={'cluster_label': 'segment_label'})
    segment_summary.to_csv(PROCESSED_PATH / 'segment_summary.csv', index=False)
    print('Risk scored customers and segment summary saved to', PROCESSED_PATH)

if __name__ == '__main__':
    main()
