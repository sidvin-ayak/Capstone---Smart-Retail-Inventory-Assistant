# Smart Retail Inventory Assistant — Week 6-7 Starter

Capstone build (Phase 3) for the Open-Source Data & AI Internship. This
repo is a **starter scaffold**: the plumbing works end-to-end on a tiny
sample dataset so you can run, demo, and extend it. Look for `TODO (intern)`
comments — those are your job for the next two weeks.

## What you're building

| Layer       | What it does                                | Tech                          |
|-------------|---------------------------------------------|-------------------------------|
| Data        | CSV → SQLite (Postgres-ready)               | pandas, sqlite3               |
| API         | REST endpoints + Swagger docs               | FastAPI, Pydantic, pytest     |
| Dashboard   | KPI cards, charts, chatbot panel            | Streamlit (Metabase optional) |
| AI Chatbot  | RAG over inventory + sales, GPT or Ollama   | LangChain, OpenAI / Ollama    |
| Forecasting | 7-day demand forecast per product           | scikit-learn LinearRegression |

## Repo layout

```
Capstone/
├── data/                # Sample CSVs (products, inventory, sales)
├── etl/                 # CSV -> SQLite loader
├── api/                 # FastAPI app
│   ├── routes/          # inventory, sales, forecast, chat
│   └── tests/           # pytest smoke tests
├── chatbot/             # LangChain RAG + LLM provider toggle
├── dashboard/           # Streamlit app (+ Metabase notes)
├── requirements.txt
├── .env.example
└── run.ps1              # Convenience commands for Windows
```

## 5-minute setup

```powershell
# 1. Create + activate a virtualenv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install deps
pip install -r requirements.txt

# 3. Copy env template and edit it
Copy-Item .env.example .env
# -> open .env, set LLM_PROVIDER to "openai" or "ollama"
#    if openai: paste your OPENAI_API_KEY
#    if ollama: make sure `ollama serve` is running and you've pulled a model
#               e.g. `ollama pull llama3.2`

# 4. Seed the database
.\run.ps1 seed
# (or: python -m etl.seed_db)

# 5. Start the API (terminal 1)
.\run.ps1 api
# Swagger UI: http://localhost:8000/docs

# 6. Start the dashboard (terminal 2)
.\run.ps1 dash
# Dashboard: http://localhost:8501
```

Smoke check from the CLI without starting the API:

```powershell
.\run.ps1 chat "What is low on stock in Electronics?"
.\run.ps1 test
```

## LLM provider toggle

The chatbot supports three providers, controlled by one env var. No code
change is needed to switch.

```env
LLM_PROVIDER=stub     # offline demo, NO external service (default)
LLM_PROVIDER=openai   # uses GPT (OPENAI_API_KEY + OPENAI_MODEL)
LLM_PROVIDER=ollama   # uses a local model (OLLAMA_MODEL, default llama3.2)
```

**`stub` mode** lets the chatbot endpoint return an answer immediately
without OpenAI credentials or a running Ollama daemon — it just formats
the retrieved RAG context. It's intended for the first day of week 6 so
you can see the full pipeline work end-to-end; before final demo you must
switch to `openai` or `ollama` for real generation.

**Setting up Ollama** (Windows):

```powershell
# 1. Download + install: https://ollama.com/download
# 2. Make sure the daemon is running (it auto-starts after install):
ollama serve            # only if it isn't already running
# 3. Pull a small model:
ollama pull llama3.2
# 4. In .env, set:
#    LLM_PROVIDER=ollama
```

If the daemon isn't running and you select `LLM_PROVIDER=ollama`, the API
returns a clear preflight error pointing you to the install steps above —
no opaque connection-refused stack trace.

## Your week-by-week checklist

### Week 6 — get the base running and extend

- [ ] Clone, install, seed, and verify all three services start.
- [ ] Open `/docs` and call every endpoint at least once.
- [ ] **Dashboard:** add a 3rd chart — revenue by category. (See TODO in
      [dashboard/app.py](dashboard/app.py).)
- [ ] **API:** add a `category` filter to `/sales/top-products`. (TODO in
      [api/routes/sales.py](api/routes/sales.py).)
- [ ] **ETL:** add a `v_daily_revenue` SQL view (TODO in
      [etl/seed_db.py](etl/seed_db.py)) and use it from the API.
- [ ] **Tests:** add pytest cases for `/forecast/{product_id}` and `/chat`
      (TODO in [api/tests/test_api.py](api/tests/test_api.py)).

### Week 7 — AI + polish

- [ ] **Chatbot:** add forecast-trend documents to the retriever (TODO in
      [chatbot/rag_pipeline.py](chatbot/rag_pipeline.py)) so the bot can
      answer "is product X trending up?".
- [ ] **Chatbot:** swap the TF-IDF retriever for a vector store (Chroma)
      with `OllamaEmbeddings` or `OpenAIEmbeddings`. Same interface,
      better recall.
- [ ] **Forecast:** clamp negatives, hold out the last 5 days, print
      MAE/RMSE (TODO in [api/routes/forecast.py](api/routes/forecast.py)).
- [ ] **Demo:** record a 3-5 minute walkthrough (slide deck deliverable).
- [ ] **Docker (stretch):** write a `docker-compose.yml` that brings up
      api + dashboard + (optionally) Metabase + Ollama.

## Architecture (matches the slide deck)

```
 CSV files ──► ETL ──► SQLite/Postgres ──► FastAPI ──► Streamlit Dashboard
                                              │
                                              └──► /chat ──► LangChain RAG
                                                                │
                                                       ┌────────┴────────┐
                                                       │                 │
                                                   OpenAI GPT       Local Ollama
```

## Troubleshooting

- **`No sales history for product …`** → run `.\run.ps1 seed` first.
- **`Connection refused` from dashboard** → API isn't running on :8000.
- **Ollama errors** → run `ollama serve` and `ollama pull llama3.2`.
- **OpenAI 401** → check `OPENAI_API_KEY` in `.env`.
- **`ModuleNotFoundError: langchain_ollama`** → `pip install -r requirements.txt`
  inside the activated venv.
- **`TypeError: _TypedDictMeta.__new__() got an unexpected keyword argument 'closed'`**
  → this comes from Altair's incompatibility with newer `typing_extensions`.
  The dashboard charts use Plotly to avoid that stack entirely; if you ever
  see this, run `pip install plotly` and reload.

## What's intentionally *not* done

The scaffold is meant to be ~60% complete. Things left for the intern:

- Real categorical filtering on sales endpoints.
- Vector-embedding RAG and forecast-aware retrieval.
- Forecast evaluation metrics (MAE/RMSE).
- More charts on the dashboard.
- Docker compose for the full stack.
- Auth on the API (FastAPI dependency injection makes this easy).
- A polished demo deck and video.
