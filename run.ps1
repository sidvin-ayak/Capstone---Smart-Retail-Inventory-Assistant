# Convenience runner for Windows / PowerShell.
# Usage:
#   .\run.ps1 seed     # (re)build SQLite DB from CSVs
#   .\run.ps1 api      # start FastAPI on :8000
#   .\run.ps1 dash     # start Streamlit dashboard on :8501
#   .\run.ps1 test     # run pytest smoke tests
#   .\run.ps1 chat "What is low on stock?"

param(
    [Parameter(Position = 0)] [string] $cmd = "help",
    [Parameter(Position = 1, ValueFromRemainingArguments = $true)] [string[]] $rest
)

switch ($cmd) {
    "seed" { python -m etl.seed_db }
    "api"  { uvicorn api.main:app --reload --port 8000 }
    "dash" { streamlit run dashboard/app.py }
    "test" { pytest -q }
    "chat" {
        $q = ($rest -join " ")
        python -m chatbot.rag_pipeline $q
    }
    default {
        Write-Output "Commands: seed | api | dash | test | chat <question>"
    }
}
