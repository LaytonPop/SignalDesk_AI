"""
爬虫触发接口。

POST /api/v1/sources/crawl —— 加载站点配置，执行爬虫抓取文章，可选择自动入库到向量库。
目前唯一有 try/except 防护的路由：ValueError 转 400，其他异常会 500。
被前端爬虫管理页使用。
"""

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
