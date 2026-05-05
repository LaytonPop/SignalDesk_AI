from fastapi import APIRouter

from intel_analyst.schemas.article import ArticleListResponse
from intel_analyst.storage.article_repository import ArticleRepository

router = APIRouter()


@router.get("/articles", response_model=ArticleListResponse)
def list_articles(limit: int = 20) -> ArticleListResponse:
    repository = ArticleRepository()
    items = repository.list_articles(limit=limit)
    return ArticleListResponse(items=items, total=len(items))
