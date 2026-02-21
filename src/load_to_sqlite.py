\
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .db import connect


DDL = """
CREATE TABLE IF NOT EXISTS sales (
  order_id TEXT PRIMARY KEY,
  order_date TEXT NOT NULL,
  order_month TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  region TEXT NOT NULL,
  channel TEXT NOT NULL,
  product_category TEXT NOT NULL,
  unit_price REAL NOT NULL,
  quantity INTEGER NOT NULL,
  discount_pct REAL NOT NULL,
  returned INTEGER NOT NULL,
  gross_revenue REAL NOT NULL,
  net_revenue REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sales_month ON sales(order_month);
CREATE INDEX IF NOT EXISTS idx_sales_region ON sales(region);
CREATE INDEX IF NOT EXISTS idx_sales_category ON sales(product_category);
"""


def main() -> None:
    p = argparse.ArgumentParser(description="Load cleaned CSV into SQLite.")
    p.add_argument("--csv", type=str, required=True)
    p.add_argument("--db", type=str, required=True)
    args = p.parse_args()

    csv_path = Path(args.csv)
    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)
    keep = [
        "order_id","order_date","order_month","customer_id","region","channel",
        "product_category","unit_price","quantity","discount_pct","returned",
        "gross_revenue","net_revenue"
    ]
    df = df[keep]

    conn = connect(db_path)
    with conn:
        conn.executescript(DDL)
        # Replace on conflict by deleting existing ids first (safe for demo)
        ids = [(x,) for x in df["order_id"].astype(str).tolist()]
        conn.executemany("DELETE FROM sales WHERE order_id = ?", ids)
        df.to_sql("sales", conn, if_exists="append", index=False)

    conn.close()
    print(f"Loaded {len(df):,} rows into {db_path}")


if __name__ == "__main__":
    main()
