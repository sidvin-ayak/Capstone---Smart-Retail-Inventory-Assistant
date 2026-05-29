"""
Smoke tests for the API. Run with: pytest -q

Pre-req: seed the DB first via `python -m etl.seed_db`.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_inventory() -> None:
    r = client.get("/inventory")
    assert r.status_code == 200
    items = r.json()
    assert len(items) > 0
    assert {"product_id", "current_stock", "status"} <= items[0].keys()


def test_low_stock_subset() -> None:
    all_items = client.get("/inventory").json()
    low = client.get("/inventory/low-stock").json()
    assert all(i["status"] in ("LOW", "OUT_OF_STOCK") for i in low)
    assert len(low) <= len(all_items)


def test_top_products() -> None:
    r = client.get("/sales/top-products?limit=3")
    assert r.status_code == 200
    assert len(r.json()) <= 3


# TODO (intern): add tests for /forecast/{product_id} and /chat.
