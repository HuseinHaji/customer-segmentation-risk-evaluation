import pandas as pd
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[1]
RAW_PATH = BASE_PATH / 'data' / 'raw'
PROCESSED_PATH = BASE_PATH / 'data' / 'processed'


def main():
    PROCESSED_PATH.mkdir(parents=True, exist_ok=True)
    customers = pd.read_csv(RAW_PATH / 'customer_master.csv')
    customers['revenue_per_order'] = customers['revenue'] / customers['number_of_orders']
    customers['payment_delay_category'] = pd.cut(customers['payment_delay'], bins=[-1, 7, 14, 30, 90], labels=['On time', 'Moderate', 'Delayed', 'High Delay'])
    customers['overdue_ratio'] = customers['overdue_amount'] / customers['revenue']
    customers['credit_utilization'] = customers['exposure_amount'] / customers['credit_limit']
    customers.to_csv(PROCESSED_PATH / 'customer_features.csv', index=False)
    print('Customer features saved to', PROCESSED_PATH)

if __name__ == '__main__':
    main()
