"""
Pluggable LLM client.

Pick provider via env var LLM_PROVIDER=stub|openai|ollama (default: stub).

- stub    -> deterministic, NO external service. Lets the chatbot demo run
             out of the box. Replace with a real LLM before submission.
- openai  -> uses OPENAI_API_KEY + OPENAI_MODEL (default gpt-4o-mini)
- ollama  -> uses OLLAMA_BASE_URL + OLLAMA_MODEL (default llama3.2)
             Requires `ollama serve` running locally and a pulled model.

The function returns a LangChain `BaseChatModel`-compatible object so the
RAG pipeline does not care which provider is active.
"""
from __future__ import annotations

import os
from dotenv import load_dotenv
load_dotenv()
from typing import Any


class OllamaUnreachableError(RuntimeError):
    """Raised when LLM_PROVIDER=ollama but the daemon is not running."""


def _ping_ollama(base_url: str, timeout: float = 2.0) -> None:
    """Friendly preflight so the intern sees a clear error, not a stack trace."""
    import requests

    try:
        r = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=timeout)
        r.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        raise OllamaUnreachableError(
            f"Ollama not reachable at {base_url}. Either:\n"
            "  1. Install Ollama from https://ollama.com/download, run "
            "`ollama serve`, then `ollama pull llama3.2`, OR\n"
            "  2. Set LLM_PROVIDER=stub in .env to use the offline demo mode, OR\n"
            "  3. Set LLM_PROVIDER=openai and provide OPENAI_API_KEY."
        ) from exc


def get_llm() -> Any:
    provider = os.getenv("LLM_PROVIDER", "stub").lower()

    if provider == "stub":
        # Sentinel — the RAG pipeline checks for this and skips the LLM call.
        return "stub"

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.2,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    if provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        _ping_ollama(base_url)

        # `langchain_ollama` is the modern package; `langchain_community.ChatOllama`
        # also works if you'd rather keep deps light.
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            base_url=base_url,
            temperature=0.2,
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER={provider!r}. Use 'stub', 'openai', or 'ollama'."
    )
