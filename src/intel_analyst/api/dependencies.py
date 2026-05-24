"""
FastAPI 依赖注入的 getter 函数。

每个 getter 创建并缓存一个 Service 实例（单例），所有路由通过
Depends(get_xxx_service) 注入。路由层不关心 Service 的初始化细节。

被所有 api/routes/*.py 引用。
"""

from functools import lru_cache

from intel_analyst.services.crawler_service import CrawlerService
from intel_analyst.services.ingestion_service import IngestionService
from intel_analyst.services.query_service import QueryService
from intel_analyst.services.report_service import ReportService


@lru_cache(maxsize=1)
def get_crawler_service() -> CrawlerService:
    """爬虫服务：加载站点配置、抓取文章、可选的入库。被 POST /sources/crawl 使用。"""
    return CrawlerService()


@lru_cache(maxsize=1)
def get_ingestion_service() -> IngestionService:
    """入库服务：将 ArticleRecord 列表切片后写入向量库。被 POST /pipeline/rebuild-index 使用。"""
    return IngestionService()


@lru_cache(maxsize=1)
def get_query_service() -> QueryService:
    """问答服务：向量检索 + LLM 生成回答。被 POST /knowledge/query 使用（最频繁）。"""
    return QueryService()


@lru_cache(maxsize=1)
def get_report_service() -> ReportService:
    """日报服务：拉取最近文章，由 LLM 生成日报。被 POST /reports/daily 使用。"""
    return ReportService()
