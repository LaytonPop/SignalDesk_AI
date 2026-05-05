from pydantic import BaseModel, Field

from intel_analyst.schemas.article import ArticleRecord
from intel_analyst.schemas.source import SourceConfig


class CrawlRequest(BaseModel):
    source_path: str | None = Field(default=None, description="Path to source config JSON.")
    source: SourceConfig | None = None
    max_articles: int | None = Field(default=None, ge=1, le=100)
    persist_raw: bool = True
    auto_ingest: bool = True


class CrawlResponse(BaseModel):
    source_name: str
    crawled_count: int
    ingested_count: int
    articles: list[ArticleRecord]
