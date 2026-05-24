"""
RAG 问答的请求/响应模型。

QueryRequest:  POST /knowledge/query 的请求体，含问题和检索数量。
QueryResponse: 返回 LLM 生成的答案、引用文章列表和检索到的文档数。
Citation:      每篇引用的文章信息（标题、URL、发表时间、内容片段）。
"""

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
