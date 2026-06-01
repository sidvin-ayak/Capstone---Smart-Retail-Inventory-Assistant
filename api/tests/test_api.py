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

# Forecast endpoint test
def test_forecast_endpoint() -> None:
    r = client.get("/forecast/P001?horizon=7")
    assert r.status_code == 200
    forecast = r.json()
    assert len(forecast) > 0
    assert all(
    "day_offset" in item and
    "predicted_units" in item
    for item in forecast
)

# Chat endpoint test
def test_chat_endpoint() -> None:
    payload = {"question": "What is low on stock?"}
    r = client.post("/chat", json=payload)
    assert r.status_code == 200
    response = r.json()
    assert "answer" in response
    assert "sources" in response
    assert isinstance(response["answer"], str)
    assert isinstance(response["sources"], list)
    
# ADDITIONAL VALIDATION TESTS    
    
# Category filter test
def test_top_products_category_filter() -> None:
    def test_top_products_category_filter() -> None:
        for category in ["Electronics", "Furniture", "Stationery"]:
            r = client.get(f"/sales/top-products?limit=10&category={category}")
            assert r.status_code == 200
            products = r.json()
            if products:
                assert all(
                    p["category"] == category
                    for p in products
                    )

# Daily revenue endpoint test
def test_daily_revenue_endpoint() -> None:
    r = client.get("/sales/daily-revenue")
    assert r.status_code == 200
    revenue = r.json()
    assert len(revenue) > 0
    assert {
        "transaction_date",
        "revenue",
        "units_sold"
    } <= revenue[0].keys()
    
