# Debian Data Ops: Retail Insights (Python + SQL + Streamlit)

A practical, problem-solving data project you can upload to GitHub.

**Problem this project solves**
Small businesses often have sales data scattered across CSV exports. This repo shows a clean workflow to:
1) generate or ingest sales CSV data,
2) validate + clean it,
3) load it into a SQLite database,
4) produce an automated KPI report with charts,
5) explore insights in a lightweight Streamlit dashboard.

This is **Linux friendly** and runs well on Debian.

---

## Tech Stack
- Python (pandas, numpy)
- SQLite (built-in)
- Streamlit dashboard
- Automated checks (basic tests)
- GitHub Actions CI (runs tests)

---

## Quick Start (Debian)
### 1) Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2) Generate sample data (or replace with your own CSV)
```bash
python -m src.generate_data --rows 30000 --out data/raw/sales.csv
```

### 3) Validate, clean, and build the SQLite database
```bash
python -m src.clean_data --infile data/raw/sales.csv --outfile data/processed/sales_clean.csv
python -m src.load_to_sqlite --csv data/processed/sales_clean.csv --db data/processed/retail.db
```

### 4) Create an automated report (KPIs + charts)
```bash
python -m src.report --db data/processed/retail.db --out reports/kpi_report.md
```

Charts are saved into `reports/figures/`.

### 5) Run the dashboard
```bash
streamlit run src/app.py
```

---

## Use Your Own Data
If you already have sales data, match these columns:
- `order_id` (string)
- `order_date` (YYYY-MM-DD)
- `customer_id` (string)
- `region` (string)
- `channel` (Online / Store / Partner)
- `product_category` (string)
- `unit_price` (number)
- `quantity` (integer)
- `discount_pct` (0-0.6)
- `returned` (0/1)

Then run the same clean + load + report pipeline.

---

## Project Structure
```
.
├── data/
│   ├── raw/
│   └── processed/
├── reports/
│   └── figures/
├── src/
│   ├── app.py
│   ├── clean_data.py
│   ├── db.py
│   ├── generate_data.py
│   ├── load_to_sqlite.py
│   └── report.py
├── tests/
│   └── test_cleaning.py
└── .github/workflows/ci.yml
```

---

## What to Showcase on LinkedIn
- Screenshot of the Streamlit dashboard
- A short post: what problem it solves, what tools you used, the KPIs you extracted
- Link to this repo in your Featured section

---

## License
MIT
