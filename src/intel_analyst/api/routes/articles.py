"""
文章列表接口。

GET /api/v1/articles?limit=20 —— 从已处理的 JSON 文件中列出最近的文章。
被前端文章列表页使用。
"""

from fastapi import APIRouter

from intel_analyst.schemas.article import ArticleListResponse
from intel_analyst.storage.article_repository import ArticleRepository

router = APIRouter()


@router.get("/articles", response_model=ArticleListResponse)
def list_articles(limit: int = 20) -> ArticleListResponse:
    repository = ArticleRepository()
    items = repository.list_articles(limit=limit)
    return ArticleListResponse(items=items, total=len(items))
