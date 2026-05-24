"""
爬虫调度服务 —— 编排爬虫工作的入口。

流程：
    1. 通过 CrawlRequest 拿到 SiteConfig（来源配置 JSON 或直接传入）
    2. 调用 GenericNewsCrawler.crawl() 抓取文章列表
    3. 如果 auto_ingest=True，调用 IngestionService 将文章写入向量库
    4. 返回 CrawlResponse（来源名、抓取数、入库数、文章列表）

被 POST /api/v1/sources/crawl 调用。
也被 mcp/server.py 的 crawl_and_ingest tool 调用。
"""

from intel_analyst.crawlers.generic_news import GenericNewsCrawler
from intel_analyst.crawlers.source_loader import SourceLoader
from intel_analyst.schemas.crawl import CrawlRequest, CrawlResponse
from intel_analyst.services.ingestion_service import IngestionService


class CrawlerService:
    def __init__(self) -> None:
        self.source_loader = SourceLoader()          # 从 JSON 文件加载站点配置
        self.crawler = GenericNewsCrawler()          # 通用的 BeautifulSoup 新闻爬虫
        self.ingestion_service = IngestionService()  # 文章入库

    def crawl(self, payload: CrawlRequest) -> CrawlResponse:
        # 解析站点配置：优先使用直接传入的 source，其次从 source_path 加载
        source = payload.source
        if source is None and payload.source_path:
            source = self.source_loader.load(payload.source_path)
        if source is None:
            raise ValueError("Either source_path or source must be provided.")

        # 执行爬取
        articles = self.crawler.crawl(
            source=source,
            max_articles=payload.max_articles,
            persist_raw=payload.persist_raw,
        )

        # 可选：自动入库到向量库
        ingested_count = 0
        if payload.auto_ingest:
            ingested_count = self.ingestion_service.ingest_articles(articles)

        return CrawlResponse(
            source_name=source.name,
            crawled_count=len(articles),
            ingested_count=ingested_count,
            articles=articles,
        )
