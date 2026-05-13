import numpy as np
import pandas as pd
from pathlib import Path

RAW_PATH = Path(__file__).resolve().parents[1] / 'data' / 'raw'
RANDOM_SEED = 3030
CUSTOMER_COUNT = 120
COUNTRIES = ['Germany', 'France', 'Italy', 'Netherlands', 'Austria']
INDUSTRIES = ['Automotive', 'Pharma', 'FMCG', 'Logistics', 'Retail']
PRODUCT_CATEGORIES = ['Machinery', 'Software', 'Chemicals', 'Packaging', 'Components']


def main():
    RAW_PATH.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(RANDOM_SEED)
    customers = []
    for i in range(1, CUSTOMER_COUNT + 1):
        revenue = round(abs(rng.normal(820000, 250000)), 2)
        margin = round(min(max(rng.normal(0.16, 0.05), 0.04), 0.35), 4)
        orders = int(max(3, rng.poisson(18)))
        avg_order_value = round(revenue / max(orders, 1), 2)
        payment_delay = round(max(0, rng.normal(12, 8)), 1)
        overdue_amount = round(revenue * rng.uniform(0.0, 0.065), 2)
        complaints = int(max(0, rng.poisson(0.9)))
        tenure_months = int(max(6, rng.integers(12, 96)))
        credit_limit = round(revenue * rng.uniform(0.45, 0.9), 2)
        exposure_amount = round(revenue * rng.uniform(0.25, 0.75), 2)
        default_flag = rng.random() < 0.08
        customers.append({
            'customer_id': f'CUST{i:03d}',
            'country': rng.choice(COUNTRIES),
            'industry': rng.choice(INDUSTRIES),
            'customer_age': int(max(1, rng.normal(7, 3))),
            'revenue': revenue,
            'margin': margin,
            'number_of_orders': orders,
            'avg_order_value': avg_order_value,
            'payment_delay': payment_delay,
            'overdue_amount': overdue_amount,
            'complaints': complaints,
            'product_category': rng.choice(PRODUCT_CATEGORIES),
            'default_flag': default_flag,
            'customer_tenure_months': tenure_months,
            'credit_limit': credit_limit,
            'exposure_amount': exposure_amount,
        })
    df = pd.DataFrame(customers)
    df.to_csv(RAW_PATH / 'customer_master.csv', index=False)
    print('Customer master data generated to', RAW_PATH)

if __name__ == '__main__':
    main()
