import json
from pathlib import Path

from intel_analyst.core.config import get_settings
from intel_analyst.schemas.article import ArticleRecord


class ArticleRepository:
    def __init__(self) -> None:
        self.settings = get_settings()

    def save_article(self, article: ArticleRecord) -> str:
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
        files = self._list_article_files()
        items: list[ArticleRecord] = []
        for file_path in files[:limit]:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            items.append(ArticleRecord.model_validate(data))
        return items

    def iter_articles(self) -> list[ArticleRecord]:
        items: list[ArticleRecord] = []
        for file_path in self._list_article_files():
            data = json.loads(file_path.read_text(encoding="utf-8"))
            items.append(ArticleRecord.model_validate(data))
        return items

    def _list_article_files(self) -> list[Path]:
        return sorted(
            self.settings.processed_data_dir.glob("*/*.json"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
