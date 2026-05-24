"""
爬虫接口的请求/响应模型。

CrawlRequest: POST /sources/crawl 的请求体，可指定站点配置来源、缓存和入库行为。
CrawlResponse: 返回爬取结果摘要和文章列表。
"""

from pydantic import BaseModel, Field

from intel_analyst.schemas.article import ArticleRecord
from intel_analyst.schemas.source import SourceConfig


class CrawlRequest(BaseModel):
    source_path: str | None = Field(default=None, description="Path to source config JSON.")
    source: SourceConfig | None = None
    max_articles: int | None = Field(default=None, ge=1, le=100)
    persist_raw: bool = True    # 是否保存原始 HTML
    auto_ingest: bool = True    # 爬取后是否自动写入向量库


class CrawlResponse(BaseModel):
    source_name: str
    crawled_count: int
    ingested_count: int
    articles: list[ArticleRecord]
