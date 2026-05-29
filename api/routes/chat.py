"""
Chat route — wires HTTP layer to the chatbot RAG pipeline.

The pipeline itself lives in `chatbot/`. This file is just transport.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.models import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    # Lazy import so the API can boot even if langchain extras are not yet
    # installed (handy for week 6 day 1).
    try:
        from chatbot.rag_pipeline import answer_question
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Chatbot dependencies not installed. Run "
                "`pip install -r requirements.txt`."
            ),
        ) from exc

    try:
        result = answer_question(req.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ChatResponse(answer=result["answer"], sources=result.get("sources", []))
