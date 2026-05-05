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
