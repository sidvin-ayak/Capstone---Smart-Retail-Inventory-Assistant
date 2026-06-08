"""Sales analytics routes."""
from __future__ import annotations

from fastapi import APIRouter, Query

from api.database import get_conn
from api.models import DailyRevenue, TopProduct
from api.models import ProductTrend

router = APIRouter(prefix="/sales", tags=["sales"])

@router.get("/daily-revenue", response_model=list[DailyRevenue])
def daily_revenue(days: int = Query(default=30, ge=1, le=365)) -> list[DailyRevenue]:
    
    sql = """
        SELECT
            transaction_date,
            revenue,
            units_sold
        FROM v_daily_revenue
        ORDER BY transaction_date DESC
        LIMIT ?
    """

    with get_conn() as conn:
        rows = conn.execute(sql, (days,)).fetchall()

    return [DailyRevenue(**dict(r)) for r in rows][::-1]



@router.get("/top-products", response_model=list[TopProduct])
def top_products(
    limit: int = Query(default=5, ge=1, le=50),
    category: str | None = Query(
        default=None,
        description="Optional category filter"
    ),
) -> list[TopProduct]:

    sql = """
        SELECT
            p.product_id,
            p.product_name,
            p.category,
            SUM(s.quantity) AS units_sold,
            SUM(s.total) AS revenue
        FROM sales s
        JOIN products p
            ON p.product_id = s.product_id
    """

    params = []

    # Optional filtering
    if category:
        sql += """
            WHERE LOWER(p.category) = LOWER(?)
        """
        params.append(category.strip())

    # Aggregation & sorting
    sql += """
        GROUP BY
            p.product_id,
            p.product_name,
            p.category
        ORDER BY revenue DESC
        LIMIT ?
    """

    params.append(limit)

    # Query execution
    with get_conn() as conn:
        rows = conn.execute(sql, tuple(params)).fetchall()

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

@router.get("/trends", response_model=list[ProductTrend])
def sales_trends() -> list[ProductTrend]:

    sql = """
    WITH daily_sales AS (
        SELECT
            product_id,
            transaction_date,
            SUM(quantity) AS units
        FROM sales
        GROUP BY product_id, transaction_date
    )
    SELECT
        p.product_id,
        p.product_name,
        COALESCE(
            (
                SELECT AVG(units)
                FROM (
                    SELECT units
                    FROM daily_sales ds
                    WHERE ds.product_id = p.product_id
                    ORDER BY transaction_date DESC
                    LIMIT 7
                )
            ),
            0
        ) AS recent_avg,
        COALESCE(
            (
                SELECT AVG(units)
                FROM (
                    SELECT units
                    FROM daily_sales ds
                    WHERE ds.product_id = p.product_id
                    ORDER BY transaction_date DESC
                    LIMIT 14 OFFSET 7
                )
            ),
            0
        ) AS previous_avg

    FROM products p
    """
    with get_conn() as conn:
        rows = conn.execute(sql).fetchall()

    trends = []

    for row in rows:
        recent = float(row["recent_avg"] or 0)
        previous = float(row["previous_avg"] or 0)
        if previous == 0:
            growth_pct = 0.0
            trend = "STABLE"
        else:
            growth_pct = ((recent - previous) / previous) * 100
            if growth_pct > 10:
                trend = "UPWARD"
            elif growth_pct < -10:
                trend = "DOWNWARD"
            else:
                trend = "STABLE"

        trends.append(
            ProductTrend(
                product_id=row["product_id"],
                product_name=row["product_name"],
                trend=trend,
                growth_pct=round(growth_pct, 2),
            )
        )
    return trends