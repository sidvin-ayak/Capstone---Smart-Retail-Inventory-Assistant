"""
Demand forecasting route.

Starter uses a tiny linear regression on day-of-year vs daily units sold per
product. Intern: extend to per-category seasonality, evaluate with MAE/RMSE,
or swap in Prophet / scikit-learn pipelines.
"""
from __future__ import annotations
from datetime import datetime
from sklearn.metrics import (mean_absolute_error, mean_squared_error)

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from sklearn.linear_model import LinearRegression

from api.database import get_conn
from api.models import ForecastPoint

router = APIRouter(prefix="/forecast", tags=["forecast"])


def _load_daily_units(product_id: str) -> pd.DataFrame:
    with get_conn() as conn:
        df = pd.read_sql_query(
            """
            SELECT transaction_date, SUM(quantity) AS units
            FROM sales
            WHERE product_id = ?
            GROUP BY transaction_date
            ORDER BY transaction_date
            """,
            conn,
            params=(product_id,),
        )
    if df.empty:
        return df
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["day_index"] = (df["transaction_date"] - df["transaction_date"].min()).dt.days
    return df


@router.get("/{product_id}", response_model=list[ForecastPoint])
def forecast_product(
    product_id: str,
    horizon: int = Query(default=5, ge=1, le=30),
) -> list[ForecastPoint]:
    df = _load_daily_units(product_id)
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No sales history for product {product_id}",
        )

    # Validation data set = Last 5 days
    validation_days = min(5, len(df) // 3)
    if validation_days > 0:
        train_df = df.iloc[:-validation_days]
        test_df = df.iloc[-validation_days:]
    else:
        train_df = df
        test_df = pd.DataFrame()

    # Model training
    X_train = train_df[["day_index"]].to_numpy()
    y_train = train_df["units"].to_numpy()
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Model evaluation
    if not test_df.empty:
        X_test = test_df[["day_index"]].to_numpy()
        y_test = test_df["units"].to_numpy()
        test_preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, test_preds)
        rmse = np.sqrt(mean_squared_error(y_test, test_preds))
        print(
            f"[FORECAST] Product={product_id} | "
            f"MAE={mae:.2f} | "
            f"RMSE={rmse:.2f}"
        )

    # Future forecast
    last_idx = int(df["day_index"].max())
    future_idx = np.arange(
        last_idx + 1,
        last_idx + 1 + horizon
    ).reshape(-1, 1)
    preds = model.predict(future_idx)

    # -ve prediction clamping
    preds = np.maximum(preds, 0)
    return [
        ForecastPoint(
            day_offset=i + 1,
            predicted_units=float(round(p, 2)),
        )
        for i, p in enumerate(preds)
    ]
