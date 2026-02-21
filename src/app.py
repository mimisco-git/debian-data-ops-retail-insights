\
from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st

DB_DEFAULT = Path("data/processed/retail.db")


@st.cache_data(show_spinner=False)
def load_df(db_path: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    return df


def main() -> None:
    st.set_page_config(page_title="Retail Insights", layout="wide")
    st.title("Retail Insights Dashboard")

    db_path = st.sidebar.text_input("SQLite DB path", value=str(DB_DEFAULT))
    if not Path(db_path).exists():
        st.warning("Database not found. Build it first with: clean_data -> load_to_sqlite.")
        st.stop()

    df = load_df(db_path)

    # Filters
    regions = ["All"] + sorted(df["region"].unique().tolist())
    cats = ["All"] + sorted(df["product_category"].unique().tolist())
    channels = ["All"] + sorted(df["channel"].unique().tolist())

    c1, c2, c3 = st.sidebar.columns(3)
    region = c1.selectbox("Region", regions)
    cat = c2.selectbox("Category", cats)
    channel = c3.selectbox("Channel", channels)

    dff = df.copy()
    if region != "All":
        dff = dff[dff["region"] == region]
    if cat != "All":
        dff = dff[dff["product_category"] == cat]
    if channel != "All":
        dff = dff[dff["channel"] == channel]

    # KPIs
    orders = len(dff)
    customers = dff["customer_id"].nunique()
    net_rev = float(dff["net_revenue"].sum())
    aov = float(dff["net_revenue"].mean()) if orders else 0.0
    return_rate = float(dff["returned"].mean()) if orders else 0.0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Orders", f"{orders:,}")
    k2.metric("Customers", f"{customers:,}")
    k3.metric("Net Revenue (₦)", f"{net_rev:,.2f}")
    k4.metric("Avg Order Value (₦)", f"{aov:,.2f}")
    k5.metric("Return Rate", f"{return_rate*100:.2f}%")

    st.divider()

    left, right = st.columns([1.1, 0.9])
    with left:
        st.subheader("Monthly Net Revenue")
        monthly = (
            dff.groupby("order_month", as_index=False)["net_revenue"]
            .sum()
            .sort_values("order_month")
        )
        st.line_chart(monthly, x="order_month", y="net_revenue")

    with right:
        st.subheader("Top Categories by Net Revenue")
        top = (
            dff.groupby("product_category", as_index=False)["net_revenue"]
            .sum()
            .sort_values("net_revenue", ascending=False)
        )
        st.bar_chart(top, x="product_category", y="net_revenue")

    st.divider()
    st.subheader("Sample Records")
    st.dataframe(dff.sort_values("order_date", ascending=False).head(200), use_container_width=True)


if __name__ == "__main__":
    main()
