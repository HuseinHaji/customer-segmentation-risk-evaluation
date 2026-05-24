import os


def test_sample_customer_master_exists():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "sample", "customer_master_sample.csv")
    assert os.path.exists(path)
