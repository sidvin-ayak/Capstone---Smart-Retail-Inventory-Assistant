"""Pydantic response/request schemas for the API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Product(BaseModel):
    product_id: str
    product_name: str
    category: str
    unit_price: float
    reorder_level: int


class InventoryItem(BaseModel):
    product_id: str
    product_name: str
    category: str
    current_stock: int
    reorder_level: int
    status: str = Field(description="OK | LOW | OUT_OF_STOCK")

class ProductTrend(BaseModel):
    product_id: str
    product_name: str
    trend: str
    growth_pct: float

class DailyRevenue(BaseModel):
    transaction_date: str
    revenue: float
    units_sold: int


class TopProduct(BaseModel):
    product_id: str
    product_name: str
    category: str
    units_sold: int
    revenue: float


class ForecastPoint(BaseModel):
    day_offset: int
    predicted_units: float


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []
