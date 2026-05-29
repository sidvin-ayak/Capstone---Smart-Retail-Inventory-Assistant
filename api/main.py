"""
FastAPI entrypoint for the Smart Retail Inventory Assistant.

Run:
    uvicorn api.main:app --reload --port 8000

Then open http://localhost:8000/docs for Swagger UI.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import chat, forecast, inventory, sales

app = FastAPI(
    title="Smart Retail Inventory Assistant API",
    version="0.1.0",
    description=(
        "Week 6-7 capstone API: inventory status, sales analytics, demand "
        "forecasting, and an AI chatbot endpoint."
    ),
)

# Streamlit dashboard runs on a different port; allow it to call us.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["meta"])
def root() -> dict:
    return {"service": "smart-retail-inventory-assistant", "docs": "/docs"}


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}


app.include_router(inventory.router)
app.include_router(sales.router)
app.include_router(forecast.router)
app.include_router(chat.router)
