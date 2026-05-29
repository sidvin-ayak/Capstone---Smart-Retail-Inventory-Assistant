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
except Exception as exc:
    st.error(f"Could not reach API: {exc}")
    st.stop()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total revenue", f"Rs {summary['revenue']:,.0f}")
k2.metric("Units sold", f"{summary['units_sold']:,}")
k3.metric("Transactions", f"{summary['transactions']:,}")
k4.metric("Items needing reorder", len(low_stock))

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
        "OK": "background-color: #d1fae5",
        "LOW": "background-color: #fef3c7",
        "OUT_OF_STOCK": "background-color: #fee2e2",
    }.get(val, "")


st.dataframe(
    inv.style.map(_color_status, subset=["status"]),
    use_container_width=True,
    hide_index=True,
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
