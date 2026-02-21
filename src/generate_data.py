\
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import random
import string

import numpy as np
import pandas as pd


REGIONS = ["Lagos", "Abuja", "Rivers", "Kano", "Enugu", "Oyo"]
CHANNELS = ["Online", "Store", "Partner"]
CATEGORIES = ["Electronics", "Accessories", "Repairs", "Groceries", "Home", "Fashion"]


def _rand_id(prefix: str, n: int = 10) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return prefix + "".join(random.choice(alphabet) for _ in range(n))


def generate(rows: int, seed: int = 7) -> pd.DataFrame:
    random.seed(seed)
    np.random.seed(seed)

    start = date.today() - timedelta(days=365)
    days = np.random.randint(0, 365, size=rows)
    order_dates = [start + timedelta(days=int(d)) for d in days]

    df = pd.DataFrame({
        "order_id": [_rand_id("ORD-", 10) for _ in range(rows)],
        "order_date": [d.isoformat() for d in order_dates],
        "customer_id": [_rand_id("CUST-", 8) for _ in range(rows)],
        "region": np.random.choice(REGIONS, size=rows, p=[0.38, 0.12, 0.12, 0.12, 0.13, 0.13]),
        "channel": np.random.choice(CHANNELS, size=rows, p=[0.55, 0.35, 0.10]),
        "product_category": np.random.choice(CATEGORIES, size=rows, p=[0.22, 0.18, 0.12, 0.18, 0.15, 0.15]),
    })

    # Pricing distribution per category
    base_price = {
        "Electronics": 85000,
        "Accessories": 9000,
        "Repairs": 14000,
        "Groceries": 4500,
        "Home": 18000,
        "Fashion": 12000,
    }
    noise = np.random.normal(loc=1.0, scale=0.35, size=rows).clip(0.25, 3.0)
    df["unit_price"] = [
        round(base_price[c] * float(n), 2) for c, n in zip(df["product_category"], noise)
    ]

    # Quantity and discount
    qty = np.random.poisson(lam=2.2, size=rows) + 1
    df["quantity"] = qty.clip(1, 10)
    disc = np.random.beta(a=2.0, b=9.0, size=rows)  # mostly small discounts
    df["discount_pct"] = disc.clip(0, 0.60).round(3)

    # Returns more likely for Electronics and Online
    base_return = np.where(df["product_category"].eq("Electronics"), 0.06, 0.025)
    channel_adj = np.where(df["channel"].eq("Online"), 0.015, 0.0)
    p = (base_return + channel_adj).clip(0, 0.20)
    df["returned"] = (np.random.rand(rows) < p).astype(int)

    # Introduce a few messy values to demonstrate cleaning
    if rows >= 1000:
        idx = np.random.choice(df.index, size=max(30, rows // 500), replace=False)
        df.loc[idx[: len(idx)//3], "discount_pct"] = 1.2  # invalid
        df.loc[idx[len(idx)//3 : 2*len(idx)//3], "quantity"] = -3  # invalid
        df.loc[idx[2*len(idx)//3 :], "order_date"] = "bad-date"  # invalid
    return df


def main() -> None:
    p = argparse.ArgumentParser(description="Generate synthetic retail sales data.")
    p.add_argument("--rows", type=int, default=30000)
    p.add_argument("--out", type=str, default="data/raw/sales.csv")
    p.add_argument("--seed", type=int, default=7)
    args = p.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    df = generate(rows=args.rows, seed=args.seed)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df):,} rows to {out}")


if __name__ == "__main__":
    main()
