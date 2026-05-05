from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class ExtractedTable(BaseModel):
    index: int
    csv_path: str
    json_preview: list[dict[str, object]] = Field(default_factory=list)
    row_count: int = 0
    column_count: int = 0


class ArticleRecord(BaseModel):
    source_name: str
    industry: str | None = None
    url: HttpUrl
    title: str
    summary: str | None = None
    content: str
    published_at: datetime | None = None
    tags: list[str] = Field(default_factory=list)
    table_paths: list[str] = Field(default_factory=list)
    extracted_tables: list[ExtractedTable] = Field(default_factory=list)
    raw_html_path: str | None = None
    captured_at: datetime
    content_hash: str


class ArticleListResponse(BaseModel):
    items: list[ArticleRecord]
    total: int
