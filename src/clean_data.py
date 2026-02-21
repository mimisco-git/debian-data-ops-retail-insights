\
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED_COLS = [
    "order_id",
    "order_date",
    "customer_id",
    "region",
    "channel",
    "product_category",
    "unit_price",
    "quantity",
    "discount_pct",
    "returned",
]


def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    out = df.copy()

    # Parse dates, drop invalid
    out["order_date"] = pd.to_datetime(out["order_date"], errors="coerce")
    out = out.dropna(subset=["order_date"])

    # Coerce numeric types
    out["unit_price"] = pd.to_numeric(out["unit_price"], errors="coerce")
    out["quantity"] = pd.to_numeric(out["quantity"], errors="coerce")
    out["discount_pct"] = pd.to_numeric(out["discount_pct"], errors="coerce")
    out["returned"] = pd.to_numeric(out["returned"], errors="coerce")

    out = out.dropna(subset=["unit_price", "quantity", "discount_pct", "returned"])

    # Fix invalid ranges
    out = out[(out["unit_price"] > 0) & (out["unit_price"] < 10_000_000)]
    out["quantity"] = out["quantity"].clip(lower=1, upper=100).astype(int)
    out["discount_pct"] = out["discount_pct"].clip(lower=0, upper=0.60).round(3)
    out["returned"] = out["returned"].clip(lower=0, upper=1).astype(int)

    # Remove duplicate order_ids (keep latest by date)
    out = out.sort_values("order_date").drop_duplicates(subset=["order_id"], keep="last")

    # Derived fields
    out["gross_revenue"] = (out["unit_price"] * out["quantity"]).round(2)
    out["net_revenue"] = (out["gross_revenue"] * (1 - out["discount_pct"])).round(2)
    out["order_month"] = out["order_date"].dt.to_period("M").astype(str)

    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Validate and clean sales CSV.")
    p.add_argument("--infile", type=str, required=True)
    p.add_argument("--outfile", type=str, required=True)
    args = p.parse_args()

    infile = Path(args.infile)
    outfile = Path(args.outfile)
    outfile.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(infile)
    clean = clean_sales(df)
    clean.to_csv(outfile, index=False)
    print(f"Cleaned rows: {len(clean):,} -> {outfile}")


if __name__ == "__main__":
    main()
