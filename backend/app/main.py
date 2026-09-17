from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.repositories import router as repositories_router

app = FastAPI(
    title="CodebaseGPT",
    version="0.1.0",
    description="A full-stack RAG application for exploring public GitHub repositories.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repositories_router)
app.include_router(chat_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "CodebaseGPT"}
