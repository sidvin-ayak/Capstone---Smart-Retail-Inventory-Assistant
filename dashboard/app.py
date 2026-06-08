"""
Streamlit dashboard for the Smart Retail Inventory Assistant.

Run (after API is up on :8000):
    streamlit run dashboard/app.py

The dashboard talks to the FastAPI service over HTTP. You can point at any
deployment by setting API_BASE_URL in .env.
"""
from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Smart Retail Inventory Assistant",
    page_icon=":package:",
    layout="wide",
)


@st.cache_data(ttl=30)
def fetch(path: str, **params) -> list | dict:
    r = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def ask_bot(question: str) -> dict:
    r = requests.post(
        f"{API_BASE_URL}/chat",
        json={"question": question},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


st.title("Smart Retail Inventory Assistant")
st.caption(f"API: {API_BASE_URL}")

# ---- KPI row ----
try:
    summary = fetch("/sales/summary")
    low_stock = fetch("/inventory/low-stock")
    trend_data = pd.DataFrame(fetch("/sales/trends"))
except Exception as exc:
    st.error(f"Could not reach API: {exc}")
    st.stop()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total revenue", f"Rs {summary['revenue']:,.0f}")
k2.metric("Units sold", f"{summary['units_sold']:,}")
k3.metric("Transactions", f"{summary['transactions']:,}")
# KPI No.4 Enhancement
out_of_stock = len([i for i in low_stock if i["status"] == "OUT_OF_STOCK"])
k4.metric("Out of Stock",out_of_stock,)

st.divider()

# Inventory health visualizer
st.subheader("Inventory Health")
inventory_health = pd.DataFrame(fetch("/inventory"))
if not inventory_health.empty:
    status_counts = (
        inventory_health["status"]
        .value_counts()
        .reset_index()
    )
    status_counts.columns = ["status","count",]
    fig = px.pie(
        status_counts,
        names="status",
        values="count",
        hole=0.45,
    )
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=20, b=20),
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
    )

st.divider()

# ---- Charts ----
left, right = st.columns(2)

with left:
    st.subheader("Daily revenue (last 30 days)")
    daily = pd.DataFrame(fetch("/sales/daily-revenue", days=30))
    if not daily.empty:
        daily["transaction_date"] = pd.to_datetime(daily["transaction_date"])
        fig = px.line(
            daily,
            x="transaction_date",
            y="revenue",
            markers=True,
            labels={"transaction_date": "Date", "revenue": "Revenue (Rs)"},
        )
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=320,# Hover behavior
        hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Top 5 products by revenue")
    top = pd.DataFrame(fetch("/sales/top-products", limit=5))
    if not top.empty:
        fig = px.bar(
            top,
            x="product_name",
            y="revenue",
            color="category",
            labels={"product_name": "Product", "revenue": "Revenue (Rs)"},
        )
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=320,# Hover behavior
        hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

# ---- Revenue by category ----

st.subheader("Revenue-based Categorical Assortment")

category_data = pd.DataFrame(fetch("/sales/top-products", limit=50))

if not category_data.empty:
    category_summary = (
        category_data.groupby("category", as_index=False)["revenue"]
        .sum()
        .sort_values(by="revenue", ascending=False)
    )

    fig = px.bar(
        category_summary,
        x="category",
        y="revenue",
        color="category",
        text="revenue",
        labels={
            "category": "Category",
            "revenue": "Revenue (Rs)"
        },
    )

    fig.update_traces(
        texttemplate='Rs %{text:,.0f}',
        textposition='outside',
        marker_line_width=1.5,
        hovertemplate=
        "<b>%{x}</b><br>" +
        "Revenue: Rs %{y:,.0f}<extra></extra>",
    )

    fig.update_layout(
        height=320,

        # Transparent dark-theme friendly background
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        # Margins
        margin=dict(l=20, r=20, t=60, b=20),

        # Better typography
        title={
            "text": "Category-wise Revenue Distribution",
            "x": 0.02,
            "xanchor": "left",
            "font": {
                "size": 22,
            }
        },

        # Axis styling
        xaxis=dict(
            title="Product Category",
            showgrid=False,
            zeroline=False,
        ),

        yaxis=dict(
            title="Revenue (Rs)",
            gridcolor="rgba(255,255,255,0.08)",
            zeroline=False,
        ),

        # Legend styling
        legend=dict(
            title="Category",
            orientation="v",
            yanchor="bottom",
            y=0.99,
            xanchor="center",
            x=2.1,
        ),

        # Hover behavior
        hovermode="x unified",

        # Smooth aesthetics
        bargap=0.35,
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# General demand trend analytics derived from the internsip backend deliverable in chatbot/rag_pipeline.py
st.subheader("Demand Trend Analytics")
upward_count = len(
    trend_data[trend_data["trend"] == "UPWARD"]
)
stable_count = len(
    trend_data[trend_data["trend"] == "STABLE"]
)
downward_count = len(
    trend_data[trend_data["trend"] == "DOWNWARD"]
)
t1, t2, t3 = st.columns(3)
t1.metric(
    "Growing Products",
    upward_count
)
t2.metric(
    "Stable Products",
    stable_count
)
t3.metric(
    "Declining Products",
    downward_count
)
if not trend_data.empty:
    fig = px.bar(
        trend_data,
        x="product_name",
        y="growth_pct",
        color="trend",
        title="Product Demand Growth (%)"
    )
    fig.update_layout(
        height=400,
        hovermode="x unified"
    )
    st.plotly_chart(
        fig,
        use_container_width=True
    )
st.dataframe(
    trend_data.sort_values(
        by="growth_pct",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)

st.divider()

# Business insight panel to interpret data for the user and give conclusions
st.subheader("Business Insights")
inv1 = pd.DataFrame(
    fetch("/inventory")
)
fastest_growing = trend_data.loc[
    trend_data["growth_pct"].idxmax()
]

fastest_declining = trend_data.loc[
    trend_data["growth_pct"].idxmin()
]

total_items = len(inv1)
healthy_items = len(
    inv1[inv1["status"] == "OK"]
)
inventory_health = (
    healthy_items / total_items * 100
    if total_items > 0
    else 0
)

critical_stock = len(
    inv1[inv1["status"] == "OUT_OF_STOCK"]
)

i1, i2, i3, i4 = st.columns(4)

i1.metric(
    "Inventory Health",
    f"{inventory_health:.1f}%"
)

i2.metric(
    "Out of Stock",
    critical_stock
)

i3.metric(
    "Top Growth",
    fastest_growing["product_name"]
)

i4.metric(
    "Top Decline",
    fastest_declining["product_name"]
)

st.info(
    f"Fastest growing product: "
    f"{fastest_growing['product_name']} "
    f"({fastest_growing['growth_pct']:.1f}% growth)"
)

st.warning(
    f"Fastest declining product: "
    f"{fastest_declining['product_name']} "
    f"({fastest_declining['growth_pct']:.1f}% change)"
)

if critical_stock > 0:
    st.error(
        f"{critical_stock} products are currently out of stock."
    )

st.divider()

# ---- Inventory table ----
st.subheader("Inventory status")
category = st.selectbox(
    "Category filter",
    ["All", "Electronics", "Furniture", "Stationery"],
)
params = {} if category == "All" else {"category": category}
inv = pd.DataFrame(fetch("/inventory", **params))

def _color_status(val: str) -> str:
    return {
        "OK": "background-color: #22c55e; color: black;",
        "LOW": "background-color: #facc15; color: black;",
        "OUT_OF_STOCK": "background-color: #ef4444; color: black;",
    }.get(val, "")

st.dataframe(
    inv.style.map(_color_status, subset=["status"]),
    use_container_width=True,
    hide_index=True,
)

st.divider()

st.subheader("Demand Forecasting")
products = pd.DataFrame(fetch("/inventory"))
selected_product = st.selectbox("Select Product",products["product_id"].tolist(),)
horizon = st.slider(
    "Forecast Horizon (Days)",
    min_value=1,
    max_value=30,
    value=7,
)
forecast = pd.DataFrame(
    fetch(
        f"/forecast/{selected_product}",
        horizon=horizon,
    )
)
if not forecast.empty:
    fig = px.line(
        forecast,
        x="day_offset",
        y="predicted_units",
        markers=True,
        labels={
            "day_offset": "Future Day",
            "predicted_units": "Predicted Units",
        },
    )
    fig.update_layout(
        height=350,
        hovermode="x unified",
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
    )
    st.dataframe(
        forecast,
        hide_index=True,
        use_container_width=True,
    )

st.divider()

# ---- Chatbot ----
st.subheader("Ask the inventory assistant")
st.caption(
    "Examples: *What's low on stock in Electronics?* — "
    "*Which product made the most revenue?* — "
    "*How many Bluetooth Headphones do we have left?*"
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for entry in st.session_state.chat_history:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

if question := st.chat_input("Type your question..."):
    st.session_state.chat_history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = ask_bot(question)
                answer = result["answer"]
                sources = result.get("sources", [])
                st.markdown(answer)
                if sources:
                    with st.expander("Sources"):
                        for s in sources:
                            st.code(s)
            except Exception as exc:
                answer = f"Sorry, the assistant failed: {exc}"
                st.error(answer)
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
