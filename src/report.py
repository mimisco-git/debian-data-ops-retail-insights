\
from __future__ import annotations

import argparse
from pathlib import Path
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

from .db import connect


def kpi(conn: sqlite3.Connection) -> dict:
    q = """
    SELECT
      COUNT(*) AS orders,
      COUNT(DISTINCT customer_id) AS customers,
      SUM(net_revenue) AS net_revenue,
      AVG(net_revenue) AS avg_order_value,
      SUM(returned) * 1.0 / COUNT(*) AS return_rate
    FROM sales;
    """
    row = conn.execute(q).fetchone()
    return {
        "orders": int(row[0]),
        "customers": int(row[1]),
        "net_revenue": float(row[2]),
        "avg_order_value": float(row[3]),
        "return_rate": float(row[4]),
    }


def top_table(conn: sqlite3.Connection, group: str, limit: int = 8) -> pd.DataFrame:
    q = f"""
    SELECT {group} AS key, SUM(net_revenue) AS net_revenue, COUNT(*) AS orders
    FROM sales
    GROUP BY {group}
    ORDER BY net_revenue DESC
    LIMIT ?;
    """
    return pd.read_sql_query(q, conn, params=(limit,))


def monthly_series(conn: sqlite3.Connection) -> pd.DataFrame:
    q = """
    SELECT order_month, SUM(net_revenue) AS net_revenue, COUNT(*) AS orders
    FROM sales
    GROUP BY order_month
    ORDER BY order_month;
    """
    df = pd.read_sql_query(q, conn)
    return df


def save_monthly_plot(df: pd.DataFrame, outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.figure()
    plt.plot(df["order_month"], df["net_revenue"])
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(outpath, dpi=160)
    plt.close()


def main() -> None:
    p = argparse.ArgumentParser(description="Generate a KPI report from SQLite.")
    p.add_argument("--db", type=str, required=True)
    p.add_argument("--out", type=str, default="reports/kpi_report.md")
    args = p.parse_args()

    db = Path(args.db)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    conn = connect(db)
    k = kpi(conn)
    top_regions = top_table(conn, "region", 6)
    top_categories = top_table(conn, "product_category", 6)
    top_channels = top_table(conn, "channel", 3)
    monthly = monthly_series(conn)
    conn.close()

    fig_path = Path("reports/figures/monthly_net_revenue.png")
    save_monthly_plot(monthly, base_path := (Path.cwd() / fig_path))

    def money(x: float) -> str:
        return f"{x:,.2f}"

    report = []
    report.append("# KPI Report")
    report.append("")
    report.append("## Summary")
    report.append("")
    report.append(f"- Orders: **{k['orders']:,}**")
    report.append(f"- Customers: **{k['customers']:,}**")
    report.append(f"- Net revenue: **₦{money(k['net_revenue'])}**")
    report.append(f"- Average order value: **₦{money(k['avg_order_value'])}**")
    report.append(f"- Return rate: **{k['return_rate']*100:.2f}%**")
    report.append("")
    report.append(f"![Monthly Net Revenue]({fig_path.as_posix()})")
    report.append("")
    report.append("## Top Regions")
    report.append("")
    report.append(top_regions.to_markdown(index=False))
    report.append("")
    report.append("## Top Categories")
    report.append("")
    report.append(top_categories.to_markdown(index=False))
    report.append("")
    report.append("## Channels")
    report.append("")
    report.append(top_channels.to_markdown(index=False))
    report.append("")
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote report to {out}")


if __name__ == "__main__":
    main()
