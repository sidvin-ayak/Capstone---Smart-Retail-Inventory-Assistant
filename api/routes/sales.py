"""Sales analytics routes."""
from __future__ import annotations

from fastapi import APIRouter, Query

from api.database import get_conn
from api.models import DailyRevenue, TopProduct

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("/daily-revenue", response_model=list[DailyRevenue])
def daily_revenue(days: int = Query(default=30, ge=1, le=365)) -> list[DailyRevenue]:
    sql = """
        SELECT transaction_date,
               SUM(total) AS revenue,
               SUM(quantity) AS units_sold
        FROM sales
        GROUP BY transaction_date
        ORDER BY transaction_date DESC
        LIMIT ?
    """
    with get_conn() as conn:
        rows = conn.execute(sql, (days,)).fetchall()
    return [DailyRevenue(**dict(r)) for r in rows][::-1]


@router.get("/top-products", response_model=list[TopProduct])
def top_products(limit: int = Query(default=5, ge=1, le=50)) -> list[TopProduct]:
    # TODO (intern): also accept an optional `category` filter, similar to
    #                /inventory?category=Electronics. Mirror the same pattern.
    sql = """
        SELECT p.product_id, p.product_name, p.category,
               SUM(s.quantity) AS units_sold,
               SUM(s.total) AS revenue
        FROM sales s
        JOIN products p ON p.product_id = s.product_id
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY revenue DESC
        LIMIT ?
    """
    with get_conn() as conn:
        rows = conn.execute(sql, (limit,)).fetchall()
    return [TopProduct(**dict(r)) for r in rows]


@router.get("/summary")
def summary() -> dict:
    """Headline KPIs for the dashboard."""
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) AS transactions,
                   COALESCE(SUM(total), 0) AS revenue,
                   COALESCE(SUM(quantity), 0) AS units_sold
            FROM sales
            """
        ).fetchone()
    return dict(row)
