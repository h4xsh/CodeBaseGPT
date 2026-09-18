import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag import answer_question, stream_question

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        return ChatResponse(
            **answer_question(
                repository_id=request.repository_id,
                question=request.question,
                messages=[message.model_dump() for message in request.messages],
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/chat/stream")
def stream_chat(request: ChatRequest):
    try:
        chunks, sources = stream_question(
            repository_id=request.repository_id,
            question=request.question,
            messages=[message.model_dump() for message in request.messages],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    def events():
        try:
            model = None
            for chunk in chunks:
                if isinstance(chunk, str):
                    content, model = chunk, model or "unknown"
                else:
                    content, model = chunk["content"], chunk["model"]
                yield f"data: {json.dumps({'type': 'token', 'content': content, 'model': model})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'sources': sources, 'model': model or 'unknown'})}\n\n"
        except RuntimeError as exc:
            yield f"data: {json.dumps({'type': 'error', 'detail': str(exc)})}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
