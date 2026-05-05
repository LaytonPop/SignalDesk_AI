from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=3)
    top_k: int = Field(default=4, ge=1, le=10)


class Citation(BaseModel):
    title: str
    url: str
    published_at: str | None = None
    snippet: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    retrieved_count: int
