from pathlib import Path
from urllib.parse import quote_plus

from intel_analyst.core.config import Settings, get_settings


def ensure_data_directories(settings: Settings) -> None:
    for path in [
        settings.data_dir,
        settings.raw_data_dir,
        settings.processed_data_dir,
        settings.table_data_dir,
        settings.report_data_dir,
        settings.vectorstore_dir,
    ]:
        path.mkdir(parents=True, exist_ok=True)


class FileStore:
    def __init__(self) -> None:
        self.settings = get_settings()
        ensure_data_directories(self.settings)

    def save_raw_html(self, source_name: str, article_url: str, html: str) -> str:
        directory = self.settings.raw_data_dir / source_name
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{quote_plus(article_url)}.html"
        path = directory / filename
        path.write_text(html, encoding="utf-8")
        return str(path)

    def save_json(self, directory: Path, filename: str, content: str) -> str:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / filename
        path.write_text(content, encoding="utf-8")
        return str(path)
