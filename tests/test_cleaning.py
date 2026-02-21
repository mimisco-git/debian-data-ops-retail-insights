\
import unittest
import pandas as pd

from src.clean_data import clean_sales

class TestCleaning(unittest.TestCase):
    def test_clean_sales_drops_bad_dates_and_clips_ranges(self):
        df = pd.DataFrame({
            "order_id": ["1","2","3"],
            "order_date": ["2025-01-01", "bad", "2025-02-02"],
            "customer_id": ["a","b","c"],
            "region": ["Lagos","Lagos","Abuja"],
            "channel": ["Online","Store","Online"],
            "product_category": ["Electronics","Home","Groceries"],
            "unit_price": [1000, 2000, 3000],
            "quantity": [1, -5, 2],
            "discount_pct": [0.1, 9.0, -1.0],
            "returned": [0, 0, 2],
        })
        out = clean_sales(df)
        # row with bad date dropped
        self.assertEqual(len(out), 2)
        self.assertTrue((out["quantity"] >= 1).all())
        self.assertTrue((out["discount_pct"].between(0, 0.60)).all())
        self.assertTrue((out["returned"].between(0, 1)).all())

if __name__ == "__main__":
    unittest.main()
