"""
文件存储工具 —— 管理 data/ 目录下的原始 HTML、JSON 和日报文件的读写。

ensure_data_directories(): 确保 data/ 下所有子目录存在。在 lifespan 启动时调用。
FileStore.save_raw_html(): 保存爬取的原始 HTML 到 data/raw/{source_name}/。
FileStore.save_json():      保存文本内容到指定路径（实际是 write_text，不限于 JSON）。

被以下模块使用：
    - main.py 的 lifespan（ensure_data_directories）
    - GenericNewsCrawler._fetch_article()（保存原始 HTML）
    - ReportService.generate_daily_report()（保存日报 MD）
"""

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
        """保存原始 HTML，文件名为 URL 编码后的文章地址。"""
        directory = self.settings.raw_data_dir / source_name
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{quote_plus(article_url)}.html"
        path = directory / filename
        path.write_text(html, encoding="utf-8")
        return str(path)

    def save_json(self, directory: Path, filename: str, content: str) -> str:
        """保存文本文件到指定目录（名为 save_json，实际保存纯文本，日报 MD 也用此方法）。"""
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / filename
        path.write_text(content, encoding="utf-8")
        return str(path)
