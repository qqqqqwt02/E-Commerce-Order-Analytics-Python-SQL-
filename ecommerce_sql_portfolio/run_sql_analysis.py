"""
E-commerce train CSVs → SQLite → three analytical questions answered in SQL.

Data: ../Ecommerce Order Dataset/train/*.csv
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TRAIN_DIR = ROOT / "Ecommerce Order Dataset" / "train"

TABLES = {
    "orders": "df_Orders.csv",
    "customers": "df_Customers.csv",
    "order_items": "df_OrderItems.csv",
    "products": "df_Products.csv",
    "payments": "df_Payments.csv",
}


def load_csv(conn: sqlite3.Connection, table: str, filename: str) -> None:
    path = TRAIN_DIR / filename
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df.to_sql(table, conn, if_exists="replace", index=False)


def build_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = OFF;")
    for table, csv_name in TABLES.items():
        load_csv(conn, table, csv_name)
    return conn


# ---------------------------------------------------------------------------
# Question 1: category revenue (JOIN + GROUP BY + ORDER BY)
# ---------------------------------------------------------------------------
SQL_Q1 = """
SELECT
    p.product_category_name AS category,
    ROUND(SUM(oi.price + oi.shipping_charges), 2) AS total_line_revenue,
    COUNT(*) AS num_line_items
FROM order_items AS oi
INNER JOIN products AS p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY total_line_revenue DESC
LIMIT 15;
"""

# ---------------------------------------------------------------------------
# Question 2: state-level average delivery lead time for delivered orders
# (JOIN + filter + date arithmetic in SQLite)
# ---------------------------------------------------------------------------
SQL_Q2 = """
SELECT
    c.customer_state AS state,
    ROUND(
        AVG(
            julianday(o.order_delivered_timestamp)
            - julianday(o.order_purchase_timestamp)
        ),
        2
    ) AS avg_delivery_days,
    COUNT(*) AS delivered_orders
FROM orders AS o
INNER JOIN customers AS c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
  AND TRIM(COALESCE(o.order_delivered_timestamp, '')) <> ''
  AND TRIM(COALESCE(o.order_purchase_timestamp, '')) <> ''
GROUP BY c.customer_state
HAVING delivered_orders >= 100
ORDER BY avg_delivery_days DESC
LIMIT 15;
"""

# ---------------------------------------------------------------------------
# Question 3: payment mix (GROUP BY + DISTINCT order counts + conditional agg)
# ---------------------------------------------------------------------------
SQL_Q3 = """
SELECT
    payment_type,
    COUNT(DISTINCT order_id) AS distinct_orders,
    ROUND(SUM(payment_value), 2) AS sum_payment_value,
    ROUND(SUM(payment_value) / COUNT(DISTINCT order_id), 2) AS avg_payment_value_per_distinct_order
FROM payments
GROUP BY payment_type
ORDER BY sum_payment_value DESC;
"""


def run_query(conn: sqlite3.Connection, title: str, question: str, sql: str) -> None:
    print("=" * 72)
    print(title)
    print("- " * 36)
    print(question.strip())
    print("- " * 36)
    print(sql.strip())
    print("- " * 36)
    df = pd.read_sql_query(sql, conn)
    pd.set_option("display.max_rows", 30)
    pd.set_option("display.width", 120)
    pd.set_option("display.max_columns", 20)
    print(df.to_string(index=False))
    print()


def main() -> None:
    conn = build_db()
    try:
        run_query(
            conn,
            "Question 1",
            "What is total line revenue (SUM of price + shipping_charges) and line-item count "
            "by product category? (Demonstrates JOIN, aggregation, ORDER BY.)",
            SQL_Q1,
        )
        run_query(
            conn,
            "Question 2",
            "For delivered orders, what is the average calendar days from purchase to delivery "
            "by customer state, only for states with at least 100 delivered orders? "
            "(Demonstrates JOIN, WHERE, HAVING, date functions.)",
            SQL_Q2,
        )
        run_query(
            conn,
            "Question 3",
            "By payment type, how many distinct orders appear, what is the sum of payment_value, "
            "and what is the ratio sum / distinct orders? "
            "(Demonstrates GROUP BY, COUNT(DISTINCT), derived metrics.)",
            SQL_Q3,
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
