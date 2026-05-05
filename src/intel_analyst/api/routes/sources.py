from fastapi import APIRouter, Depends, HTTPException

from intel_analyst.api.dependencies import get_crawler_service
from intel_analyst.schemas.crawl import CrawlRequest, CrawlResponse
from intel_analyst.services.crawler_service import CrawlerService

router = APIRouter()


@router.post("/crawl", response_model=CrawlResponse)
def crawl_source(
    payload: CrawlRequest,
    crawler_service: CrawlerService = Depends(get_crawler_service),
) -> CrawlResponse:
    try:
        return crawler_service.crawl(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
