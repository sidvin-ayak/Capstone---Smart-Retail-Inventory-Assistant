"""Inventory + product routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.database import get_conn
from api.models import InventoryItem, Product

router = APIRouter(prefix="/inventory", tags=["inventory"])


def _stock_status(current: int, reorder: int) -> str:
    if current <= 0:
        return "OUT_OF_STOCK"
    if current <= reorder:
        return "LOW"
    return "OK"


@router.get("", response_model=list[InventoryItem])
def list_inventory(category: str | None = None) -> list[InventoryItem]:
    sql = """
        SELECT p.product_id, p.product_name, p.category,
               i.current_stock, p.reorder_level
        FROM inventory i
        JOIN products p ON p.product_id = i.product_id
    """
    params: list = []
    if category:
        sql += " WHERE p.category = ?"
        params.append(category)
    sql += " ORDER BY p.product_id"

    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()

    return [
        InventoryItem(
            product_id=r["product_id"],
            product_name=r["product_name"],
            category=r["category"],
            current_stock=r["current_stock"],
            reorder_level=r["reorder_level"],
            status=_stock_status(r["current_stock"], r["reorder_level"]),
        )
        for r in rows
    ]


@router.get("/low-stock", response_model=list[InventoryItem])
def low_stock() -> list[InventoryItem]:
    """Items at or below their reorder level."""
    items = list_inventory()
    return [i for i in items if i.status in ("LOW", "OUT_OF_STOCK")]


@router.get("/products", response_model=list[Product])
def list_products() -> list[Product]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT product_id, product_name, category, unit_price, reorder_level "
            "FROM products ORDER BY product_id"
        ).fetchall()
    return [Product(**dict(r)) for r in rows]


@router.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str) -> Product:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT product_id, product_name, category, unit_price, reorder_level "
            "FROM products WHERE product_id = ?",
            (product_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return Product(**dict(row))
