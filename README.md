# Smart Retail Inventory Assistant

An AI-powered retail inventory intelligence platform that combines
inventory analytics, demand forecasting, semantic search, and
LLM-assisted querying to help retailers make data-driven inventory
and replenishment decisions.

## Key Achievements

- Built an end-to-end AI-powered retail inventory analytics platform.
- Implemented semantic search using Chroma Vector Database and Nomic embeddings.
- Developed a Retrieval-Augmented Generation (RAG) chatbot for inventory intelligence.
- Added demand forecasting using Linear Regression.
- Introduced forecasting evaluation using MAE and RMSE.
- Implemented trend analytics for product demand monitoring.
- Developed interactive business intelligence dashboards using Streamlit and Plotly.
- Achieved complete API test coverage for core services.

## Features
### Inventory Management
- Real-time inventory monitoring
- Low-stock and reorder detection
- Inventory status classification
- Category-based inventory filtering
### Sales Analytics
- Revenue tracking
- Product performance analysis
- Category-wise revenue distribution
- Daily revenue trend visualization
### Demand Forecasting
- 7-day demand forecasting
- Linear Regression forecasting model
- MAE and RMSE evaluation metrics
- Negative prediction handling
- Historical trend analysis
### AI Assistant 
- Retrieval-Augmented Generation (RAG)
- Chroma Vector Database
- Semantic search using embeddings
- Ollama / OpenAI support
- Natural language inventory querying

## Dashboard Preview

<img width="1917" height="432" alt="image" src="https://github.com/user-attachments/assets/a90ce413-7b8c-41ff-90b7-2807ce377951" />
<img width="1918" height="781" alt="image" src="https://github.com/user-attachments/assets/52efb03e-d16b-4044-835b-49a037ce93f3" />
<img width="1918" height="718" alt="image" src="https://github.com/user-attachments/assets/76f65556-410b-4b02-926a-4994a01a0d19" />
<img width="1918" height="682" alt="image" src="https://github.com/user-attachments/assets/a383f029-2cf7-4fe9-8a7c-120ff02b8696" />
<img width="1918" height="923" alt="image" src="https://github.com/user-attachments/assets/89fac116-adf7-4339-9c93-ee43c56c4ab6" />
<img width="1917" height="737" alt="image" src="https://github.com/user-attachments/assets/8b59b1a3-5d81-49a8-bce6-36af73ce86e5" />
<img width="1907" height="667" alt="image" src="https://github.com/user-attachments/assets/cc602e42-a6e7-42c3-b0eb-0428a9525b53" />
<img width="1918" height="927" alt="image" src="https://github.com/user-attachments/assets/ad0766cc-1521-4f54-a1a7-ba83f0f4ea7c" />
<img width="1918" height="1077" alt="image" src="https://github.com/user-attachments/assets/1e5975ef-c560-41ba-808d-3b9dec9d813d" />
<img width="1918" height="922" alt="image" src="https://github.com/user-attachments/assets/3675b573-4f6a-4421-91dd-ddb361d0e660" />
<img width="1918" height="913" alt="image" src="https://github.com/user-attachments/assets/2542bd2a-37de-418e-b249-cbc2c61cdf42" />

## Project Architecture
                         ┌───────────────────────┐
                         │   Retail CSV Files    │
                         │ Products • Sales •    │
                         │ Inventory Data        │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │     ETL Pipeline      │
                         │ Data Cleaning &       │
                         │ Transformation        │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │    SQLite Database    │
                         │ Inventory • Sales •   │
                         │ Forecast Data         │
                         └───────────┬───────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
       ┌──────────────────────┐        ┌──────────────────────┐
       │    FastAPI Backend   │        │   Chroma Vector DB   │
       │ REST API Services    │◄──────►│ Semantic Retrieval   │
       └───────────┬──────────┘        └───────────┬──────────┘
                   │                               │
                   ▼                               ▼
       ┌──────────────────────┐       ┌──────────────────────┐
       │  Analytics Engine    │       │   RAG Chatbot        │
       │ KPI Computation      │       │ LangChain + Ollama   │
       │ Business Insights    │       │ Context Retrieval    │
       └───────────┬──────────┘       └───────────┬──────────┘
                   │                               │
                   └───────────────┬───────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │   Streamlit Dashboard      │
                    │                            │
                    │ • KPI Monitoring           │
                    │ • Revenue Analytics        │
                    │ • Inventory Tracking       │
                    │ • Demand Forecasting       │
                    │ • AI-Powered Querying      │
                    └────────────────────────────┘
## Tech

### Backend
- FastAPI
- Pydantic
- SQLite
  
### Machine Learning
- Pandas
- NumPy
  
### Data Engineering
- Scikit-learn
- Linear Regression

### AI/NLP
- LangChain
- ChromaDB
- Ollama
- OpenAI
- Nomic Embeddings

### Frontend
- Streamlit
- Plotly

## Project Structure 

| Component                 | Purpose                                                                                                                        | Technologies                |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | --------------------------- |
| **Data Ingestion & ETL**  | Extracts retail data from CSV sources, performs transformation and validation, and loads structured data into the database.    | Pandas, SQLite              |
| **Database Layer**        | Stores inventory, product, sales, forecasting, and analytical datasets with a schema designed for future PostgreSQL migration. | SQLite, SQL                 |
| **Backend API**           | Provides RESTful services for inventory management, sales analytics, forecasting, and AI-powered querying.                     | FastAPI, Pydantic           |
| **Analytics Engine**      | Computes KPIs, category-level performance metrics, revenue analytics, and business insights.                                   | Pandas, SQL                 |
| **Forecasting Engine**    | Generates demand forecasts using historical sales trends with evaluation metrics for model performance.                        | Scikit-Learn, NumPy         |
| **AI Assistant (RAG)**    | Enables natural-language querying over inventory, sales, and trend data using retrieval-augmented generation.                  | LangChain, ChromaDB, Ollama |
| **Vector Search Layer**   | Performs semantic retrieval using embeddings for improved contextual understanding and answer relevance.                       | ChromaDB, Nomic Embeddings  |
| **Interactive Dashboard** | Visualizes KPIs, forecasts, inventory health, business insights, and chatbot interactions.                                     | Streamlit, Plotly           |
| **Testing & Validation**  | Ensures endpoint reliability, forecasting stability, and chatbot functionality.                                                | Pytest                      |

## Implemented Enhancements

### Forecasting Enhancements
- Added 5-day holdout validation
- Added MAE evaluation metric
- Added RMSE evaluation metric
- Added negative prediction clamping

### RAG Improvements
- Migrated from TF-IDF retrieval to Chroma vector search
- Integrated Nomic embeddings via Ollama
- Added semantic retrieval capability
- Added product demand trend documents

### Dashboard Improvements
- Revenue by category visualization
- Category filtering support
- Trend analytics dashboard
- Enhanced KPI reporting
- Inventory status highlighting

## API Endpoints

### Inventory Management
| Method | Endpoint                           | Description                                                                 |
| ------ | ---------------------------------- | --------------------------------------------------------------------------- |
| GET    | `/inventory`                       | Retrieve complete inventory status with stock levels and reorder indicators |
| GET    | `/inventory/low-stock`             | Retrieve products currently below their reorder threshold                   |
| GET    | `/inventory/products`              | Retrieve all available product information                                  |
| GET    | `/inventory/products/{product_id}` | Retrieve detailed information for a specific product                        |

### Sales Analytics
| Method | Endpoint               | Description                                                                |
| ------ | ---------------------- | -------------------------------------------------------------------------- |
| GET    | `/sales/daily-revenue` | Retrieve daily revenue and units sold over a selected period               |
| GET    | `/sales/top-products`  | Retrieve top-performing products ranked by revenue                         |
| GET    | `/sales/summary`       | Retrieve key business KPIs including revenue, transactions, and units sold |
| GET    | `/sales/trends`        | Retrieve product-level demand trend analysis (Upward, Stable, Downward)    |

### Demand Forecasting
| Method | Endpoint                 | Description                                                                  |
| ------ | ------------------------ | ---------------------------------------------------------------------------- |
| GET    | `/forecast/{product_id}` | Generate demand forecasts for a selected product using historical sales data |

### Chatbot 
| Method | Endpoint | Description                                                                             |
| ------ | -------- | --------------------------------------------------------------------------------------- |
| POST   | `/chat`  | Natural-language querying over inventory, sales, trends, and forecasting data using RAG |

## Design Decisions

### Why Chroma?
Used Chroma for lightweight local vector retrieval and semantic search.

### Why Ollama?
Allows completely local inference without external API costs.

### Why SQLite?
Simple deployment and migration-ready schema for PostgreSQL.

### Why Linear Regression?
Provides interpretable baseline demand forecasting with minimal computational overhead.

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
