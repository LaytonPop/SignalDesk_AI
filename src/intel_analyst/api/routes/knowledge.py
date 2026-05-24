"""
知识库问答接口（RAG 查询）。

POST /api/v1/knowledge/query —— 接收用户问题，在向量库中检索相关文档，
然后将文档上下文和问题一起发给 LLM 生成带引用的回答。
这是最核心的业务端点，被前端问答框使用。
"""

from fastapi import APIRouter, Depends

from intel_analyst.api.dependencies import get_query_service
from intel_analyst.schemas.query import QueryRequest, QueryResponse
from intel_analyst.services.query_service import QueryService

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query_knowledge(
    payload: QueryRequest,
    query_service: QueryService = Depends(get_query_service),
) -> QueryResponse:
    return query_service.query(payload)
