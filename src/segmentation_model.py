import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.cluster import KMeans

BASE_PATH = Path(__file__).resolve().parents[1]
PROCESSED_PATH = BASE_PATH / 'data' / 'processed'


def label_segments(df, labels):
    df['cluster_label'] = df['cluster'].map(labels)
    return df


def choice_labels(centroids):
    labels = {}
    for cluster_id, center in enumerate(centroids):
        revenue = center[0]
        overdue = center[1]
        delay = center[2]
        if revenue > 900000 and overdue < 0.04 and delay < 15:
            labels[cluster_id] = 'High Value / Low Risk'
        elif revenue > 900000 and overdue >= 0.04:
            labels[cluster_id] = 'High Value / Watchlist'
        elif revenue < 600000 and overdue < 0.03:
            labels[cluster_id] = 'Low Value / Stable'
        elif revenue < 600000 and overdue >= 0.05:
            labels[cluster_id] = 'Low Value / High Risk'
        else:
            labels[cluster_id] = 'Growth Potential'
    return labels


def main():
    customers = pd.read_csv(PROCESSED_PATH / 'customer_features.csv')
    features = customers[['revenue', 'overdue_ratio', 'payment_delay', 'margin']].fillna(0)
    model = KMeans(n_clusters=5, random_state=3040, n_init=10)
    customers['cluster'] = model.fit_predict(features)
    labels = choice_labels(model.cluster_centers_)
    customers = label_segments(customers, labels)
    customers.to_csv(PROCESSED_PATH / 'customer_segments.csv', index=False)
    print('Customer segments saved to', PROCESSED_PATH)

if __name__ == '__main__':
    main()
