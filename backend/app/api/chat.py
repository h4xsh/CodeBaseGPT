from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return ChatResponse(
        answer="This is a placeholder response from the Phase 1 FastAPI foundation.",
        sources=[
            {
                "file_path": "README.md",
                "snippet": "Repository context will be inserted here during later phases.",
            }
        ],
    )
