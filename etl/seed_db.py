"""
ETL: load the CSV files in data/ into a SQLite database.

Default DB: ./capstone.db (SQLite). Set DATABASE_URL in .env to point at
PostgreSQL once you graduate from SQLite (e.g. postgresql://user:pw@host/db).

Run:
    python -m etl.seed_db
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DEFAULT_SQLITE_PATH = ROOT / "capstone.db"


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS products (
    product_id      TEXT PRIMARY KEY,
    product_name    TEXT NOT NULL,
    category        TEXT NOT NULL,
    unit_price      REAL NOT NULL,
    reorder_level   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory (
    product_id      TEXT PRIMARY KEY REFERENCES products(product_id),
    current_stock   INTEGER NOT NULL,
    last_updated    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sales (
    transaction_id      TEXT PRIMARY KEY,
    transaction_date    TEXT NOT NULL,
    product_id          TEXT NOT NULL REFERENCES products(product_id),
    quantity            INTEGER NOT NULL,
    unit_price          REAL NOT NULL,
    total               REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(transaction_date);
CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id);
"""


def get_sqlite_path() -> Path:
    url = os.getenv("DATABASE_URL", "")
    if url.startswith("sqlite:///"):
        return Path(url.replace("sqlite:///", "", 1))
    return DEFAULT_SQLITE_PATH


def seed_sqlite() -> Path:
    db_path = get_sqlite_path()
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)

        products = pd.read_csv(DATA_DIR / "products.csv")
        inventory = pd.read_csv(DATA_DIR / "inventory.csv")
        sales = pd.read_csv(DATA_DIR / "sales.csv")

        products.to_sql("products", conn, if_exists="append", index=False)
        inventory.to_sql("inventory", conn, if_exists="append", index=False)
        sales.to_sql("sales", conn, if_exists="append", index=False)

        # TODO (intern): add a derived view e.g. v_daily_revenue that the
        # dashboard can query directly instead of recomputing in Python.
        # Example:
        #   CREATE VIEW v_daily_revenue AS
        #   SELECT transaction_date, SUM(total) AS revenue
        #   FROM sales GROUP BY transaction_date;
        conn.commit()
    finally:
        conn.close()

    return db_path


if __name__ == "__main__":
    path = seed_sqlite()
    print(f"Seeded SQLite database at: {path}")
