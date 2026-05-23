from intel_analyst.services.crawler_service import CrawlerService
from intel_analyst.services.ingestion_service import IngestionService
from intel_analyst.services.query_service import QueryService
from intel_analyst.services.report_service import ReportService

from functools import lru_cache

@lru_cache(maxsize=1)
def get_crawler_service() -> CrawlerService:
    return CrawlerService()

@lru_cache(maxsize=1)
def get_ingestion_service() -> IngestionService:
    return IngestionService()

@lru_cache(maxsize=1)
def get_query_service() -> QueryService:
    return QueryService()

@lru_cache(maxsize=1)
def get_report_service() -> ReportService:
    return ReportService()
