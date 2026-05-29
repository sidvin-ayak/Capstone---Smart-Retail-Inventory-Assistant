"""
LangChain RAG pipeline over our retail data.

Strategy (deliberately simple for week 6-7):
1. Pull rows from SQLite and turn each row into a one-sentence "document".
2. Index documents with a TF-IDF retriever (no embedding API needed).
3. Retrieve top-K and stuff into the chat prompt.
4. Send to the configured LLM (OpenAI or Ollama).

Intern extension ideas (TODOs throughout):
- Swap TF-IDF for vector embeddings (Chroma + OllamaEmbeddings / OpenAIEmbeddings).
- Add per-product chunks combining inventory + recent sales velocity.
- Add a re-ranker stage.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Iterable

from langchain_community.retrievers import TFIDFRetriever
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser

from api.database import get_conn
from chatbot.llm_client import get_llm
from chatbot.prompts import CHAT_PROMPT

TOP_K = 6


def _build_documents() -> list[Document]:
    """Pull current state from the DB and emit one Document per fact."""
    docs: list[Document] = []

    with get_conn() as conn:
        # Inventory snapshot, one doc per product.
        rows = conn.execute(
            """
            SELECT p.product_id, p.product_name, p.category, p.unit_price,
                   p.reorder_level, i.current_stock
            FROM products p
            JOIN inventory i ON i.product_id = p.product_id
            """
        ).fetchall()
        for r in rows:
            status = (
                "OUT_OF_STOCK" if r["current_stock"] == 0
                else "LOW" if r["current_stock"] <= r["reorder_level"]
                else "OK"
            )
            text = (
                f"Product {r['product_id']} '{r['product_name']}' "
                f"(category: {r['category']}, price: Rs {r['unit_price']:.2f}). "
                f"Current stock: {r['current_stock']} units. "
                f"Reorder level: {r['reorder_level']}. Stock status: {status}."
            )
            docs.append(
                Document(
                    page_content=text,
                    metadata={"source": f"inventory:{r['product_id']}"},
                )
            )

        # Top sellers (last 30 days) — one doc each.
        top = conn.execute(
            """
            SELECT p.product_id, p.product_name, p.category,
                   SUM(s.quantity) AS units_sold,
                   SUM(s.total) AS revenue
            FROM sales s
            JOIN products p ON p.product_id = s.product_id
            GROUP BY p.product_id, p.product_name, p.category
            ORDER BY revenue DESC
            LIMIT 10
            """
        ).fetchall()
        for r in top:
            text = (
                f"Sales total for product {r['product_id']} '{r['product_name']}' "
                f"(category: {r['category']}): {r['units_sold']} units sold, "
                f"revenue Rs {r['revenue']:.2f} over the recorded period."
            )
            docs.append(
                Document(
                    page_content=text,
                    metadata={"source": f"sales:{r['product_id']}"},
                )
            )

        # Category roll-up.
        cats = conn.execute(
            """
            SELECT p.category,
                   SUM(s.quantity) AS units_sold,
                   SUM(s.total) AS revenue
            FROM sales s
            JOIN products p ON p.product_id = s.product_id
            GROUP BY p.category
            """
        ).fetchall()
        for r in cats:
            text = (
                f"Category {r['category']} totals: {r['units_sold']} units "
                f"sold, revenue Rs {r['revenue']:.2f}."
            )
            docs.append(
                Document(
                    page_content=text,
                    metadata={"source": f"category:{r['category']}"},
                )
            )

    # TODO (intern): add documents for daily trends (e.g. last 7 days vs prior 7
    # days) and for forecast outputs so the bot can answer "is X trending up?"
    return docs


@lru_cache(maxsize=1)
def _retriever() -> TFIDFRetriever:
    docs = _build_documents()
    return TFIDFRetriever.from_documents(docs, k=TOP_K)


def reset_index() -> None:
    """Call this from the intern's ETL job if the DB is reseeded."""
    _retriever.cache_clear()


def _format_context(docs: Iterable[Document]) -> str:
    return "\n".join(f"- {d.page_content}" for d in docs)


def _stub_answer(question: str, docs: list[Document]) -> str:
    """Offline fallback: format the retrieved facts as a readable answer.

    This is intentionally dumb — it just lists the top retrieved facts.
    Good enough to demo the pipeline before plugging in a real LLM.
    """
    if not docs:
        return "I don't know — no relevant data was found."
    bullets = "\n".join(f"- {d.page_content}" for d in docs[:4])
    return (
        f"(stub mode — set LLM_PROVIDER=openai or ollama for real generation)\n"
        f"Here is what the data says about: \"{question}\"\n{bullets}"
    )


def answer_question(question: str) -> dict:
    retriever = _retriever()
    docs = retriever.invoke(question)
    context = _format_context(docs)

    llm = get_llm()
    if llm == "stub":
        answer = _stub_answer(question, docs)
    else:
        chain = CHAT_PROMPT | llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})

    return {
        "answer": answer.strip(),
        "sources": [d.metadata.get("source", "") for d in docs],
    }


if __name__ == "__main__":
    # Quick CLI smoke check: `python -m chatbot.rag_pipeline`
    import sys

    q = " ".join(sys.argv[1:]) or "What is low on stock in Electronics?"
    print(f"Q: {q}")
    out = answer_question(q)
    print(f"A: {out['answer']}")
    print(f"Sources: {out['sources']}")
