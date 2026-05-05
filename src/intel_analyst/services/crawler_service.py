from intel_analyst.crawlers.generic_news import GenericNewsCrawler
from intel_analyst.crawlers.source_loader import SourceLoader
from intel_analyst.schemas.crawl import CrawlRequest, CrawlResponse
from intel_analyst.services.ingestion_service import IngestionService


class CrawlerService:
    def __init__(self) -> None:
        self.source_loader = SourceLoader()
        self.crawler = GenericNewsCrawler()
        self.ingestion_service = IngestionService()

    def crawl(self, payload: CrawlRequest) -> CrawlResponse:
        source = payload.source
        if source is None and payload.source_path:
            source = self.source_loader.load(payload.source_path)
        if source is None:
            raise ValueError("Either source_path or source must be provided.")

        articles = self.crawler.crawl(
            source=source,
            max_articles=payload.max_articles,
            persist_raw=payload.persist_raw,
        )
        ingested_count = 0
        if payload.auto_ingest:
            ingested_count = self.ingestion_service.ingest_articles(articles)

        return CrawlResponse(
            source_name=source.name,
            crawled_count=len(articles),
            ingested_count=ingested_count,
            articles=articles,
        )
