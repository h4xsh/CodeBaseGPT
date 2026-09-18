from typing import List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class RepositoryCreateRequest(BaseModel):
    github_url: HttpUrl = Field(..., description="Public GitHub repository URL")

    @field_validator("github_url")
    @classmethod
    def validate_github_url(cls, value):
        url = str(value)
        if "github.com" not in url:
            raise ValueError("Repository URL must be a valid GitHub URL.")
        return value


class RepositoryStatus(BaseModel):
    repository_id: str
    status: Literal["pending", "processing", "ready", "failed"]
    message: Optional[str] = None


class RepositoryResponse(RepositoryStatus):
    github_url: Optional[str] = None
    local_path: Optional[str] = None


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    repository_id: str
    question: str = Field(..., min_length=1)
    messages: List[ChatMessage] = Field(default_factory=list)


class SourceItem(BaseModel):
    file_path: str
    snippet: str
    chunk_index: int
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem] = Field(default_factory=list)
    model: str


class ErrorResponse(BaseModel):
    detail: str
