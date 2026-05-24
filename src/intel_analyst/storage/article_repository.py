"""
文章仓库 —— 对 data/processed/ 目录下 JSON 文件的读写封装。

每篇文章存为一个 JSON 文件，按 source_name 分子目录，文件名为 content_hash.json。
被以下模块使用：
    - GenericNewsCrawler._fetch_article() → save_article() 保存爬取结果
    - IngestionService.rebuild_index() → iter_articles() 全量读取重建索引
    - ReportService.generate_daily_report() → iter_articles() 读取文章生成日报
    - GET /articles → list_articles() 浏览文章列表
"""

import json
from pathlib import Path

from intel_analyst.core.config import get_settings
from intel_analyst.schemas.article import ArticleRecord


class ArticleRepository:
    def __init__(self) -> None:
        self.settings = get_settings()

    def save_article(self, article: ArticleRecord) -> str:
        """将一篇文章序列化为 JSON 文件保存，返回文件路径。"""
        source_dir = self.settings.processed_data_dir / article.source_name
        source_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{article.content_hash}.json"
        path = source_dir / filename
        path.write_text(
            json.dumps(article.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return str(path)

    def list_articles(self, limit: int = 20) -> list[ArticleRecord]:
        """返回最近的文章列表，最多 limit 篇。"""
        files = self._list_article_files()
        items: list[ArticleRecord] = []
        for file_path in files[:limit]:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            items.append(ArticleRecord.model_validate(data))
        return items

    def iter_articles(self) -> list[ArticleRecord]:
        """返回所有已处理文章的完整列表（一次性加载到内存）。"""
        items: list[ArticleRecord] = []
        for file_path in self._list_article_files():
            data = json.loads(file_path.read_text(encoding="utf-8"))
            items.append(ArticleRecord.model_validate(data))
        return items

    def _list_article_files(self) -> list[Path]:
        """递归扫描 processed_data_dir 下所有 JSON 文件，按修改时间降序排列。"""
        return sorted(
            self.settings.processed_data_dir.glob("*/*.json"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
