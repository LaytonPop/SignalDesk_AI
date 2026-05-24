"""
文章相关的数据结构。

ArticleRecord: 爬取后清洗完成的一篇文章，包含标题、内容、摘要、标签、发布时间、
            抓取时间、内容哈希、提取的表格等。贯穿整个管道：爬虫产出 → 文件存储 → 向量入库。
ExtractedTable: HTML 表格提取结果，含行列数和 CSV 路径。
ArticleListResponse: GET /articles 的返回体。
"""

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
