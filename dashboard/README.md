# Dashboard

This folder contains a **Streamlit** dashboard that calls the FastAPI
backend over HTTP. It's the simplest path to a working demo for week 6-7.

## Run

```powershell
# Make sure the API is running first (port 8000)
streamlit run dashboard/app.py
```

Streamlit opens on http://localhost:8501.

## Optional: Metabase

If you want to use **Metabase** (mentioned in the slide deck) instead of /
in addition to Streamlit:

1. Start Metabase via Docker:
   ```powershell
   docker run -d -p 3000:3000 --name metabase metabase/metabase
   ```
2. Open http://localhost:3000 and create an admin user.
3. Add the SQLite file `capstone.db` (at the repo root) as a data source.
4. Build charts on the `sales`, `inventory`, `products` tables. The slide
   deck calls for >=5 meaningful charts + KPI cards.

The Streamlit app stays useful for the chatbot panel — Metabase doesn't host
the LLM call.
