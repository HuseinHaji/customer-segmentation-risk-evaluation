import pandas as pd
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[1]
PROCESSED_PATH = BASE_PATH / 'data' / 'processed'
POWERBI_PATH = BASE_PATH / 'data' / 'powerbi'


def main():
    POWERBI_PATH.mkdir(parents=True, exist_ok=True)
    customers = pd.read_csv(PROCESSED_PATH / 'customer_segments.csv')
    risk = pd.read_csv(PROCESSED_PATH / 'risk_scored_customers.csv')
    powerbi = customers.merge(risk[['customer_id', 'risk_score', 'risk_category']], on='customer_id', how='left')
    powerbi.to_csv(POWERBI_PATH / 'powerbi_customer_dashboard.csv', index=False)
    print('Power BI file exported to', POWERBI_PATH)

if __name__ == '__main__':
    main()
