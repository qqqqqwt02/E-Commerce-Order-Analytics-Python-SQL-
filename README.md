# E-commerce SQL Portfolio (Python + SQLite)

Loads CSV files from `Ecommerce Order Dataset/train/` into an in-memory SQLite database and answers **three analytical questions** with standard SQL. Suitable as a small GitHub portfolio piece for SQL skills.

## Setup

```bash
cd ecommerce_sql_portfolio
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python run_sql_analysis.py
```

The script prints each question in English, the SQL statement, and the result table.

## Questions at a glance

| # | SQL techniques | Summary |
|---|----------------|---------|
| 1 | `JOIN`, `GROUP BY`, `ORDER BY` | Revenue and line-item counts by product category |
| 2 | `JOIN`, `WHERE`, `HAVING`, date math | Average delivery days by state for delivered orders (`julianday` difference) |
| 3 | `GROUP BY`, `COUNT(DISTINCT …)` | Distinct orders, total payment amount, and amount per distinct order by payment type |

## Data path

By default, CSVs are read from: `../Ecommerce Order Dataset/train/df_*.csv` (relative to this folder).

## Dependencies

- Python 3.10+
- `pandas` (for `read_csv`, `to_sql`, `read_sql_query`)
- `sqlite3` (standard library)
