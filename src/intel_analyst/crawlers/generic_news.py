import hashlib
import logging
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from intel_analyst.core.config import get_settings
from intel_analyst.crawlers.auth import authenticate_requests, login_with_selenium
from intel_analyst.crawlers.base import BaseCrawler
from intel_analyst.processing.html_tables import extract_tables_from_html
from intel_analyst.schemas.article import ArticleRecord
from intel_analyst.schemas.source import SourceConfig
from intel_analyst.storage.article_repository import ArticleRepository
from intel_analyst.storage.file_store import FileStore

logger = logging.getLogger(__name__)


class GenericNewsCrawler(BaseCrawler):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.file_store = FileStore()
        self.article_repository = ArticleRepository()

    def crawl(
        self,
        source: SourceConfig,
        max_articles: int | None = None,
        persist_raw: bool = True,
    ) -> list[ArticleRecord]:
        session = self._create_session(source)
        response = session.get(str(source.list_url), headers=source.default_headers, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select(source.list_item_selector)
        limit = max_articles or source.max_articles
        articles: list[ArticleRecord] = []

        for item in items[:limit]:
            link_node = item.select_one(source.article_link_selector)
            if not link_node or not link_node.get("href"):
                continue

            article_url = urljoin(str(source.base_url), link_node["href"])
            try:
                article = self._fetch_article(session, source, article_url, persist_raw=persist_raw)
                articles.append(article)
            except Exception as exc:
                logger.warning("Failed to crawl article %s: %s", article_url, exc)

        return articles

    def _create_session(self, source: SourceConfig) -> requests.Session:
        if source.auth.mode == "selenium":
            return login_with_selenium(source.auth)
        return authenticate_requests(source.auth).session

    def _fetch_article(
        self,
        session: requests.Session,
        source: SourceConfig,
        article_url: str,
        persist_raw: bool = True,
    ) -> ArticleRecord:
        response = session.get(article_url, headers=source.default_headers, timeout=20)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        title = self._extract_text(soup, source.article_title_selector) or "Untitled"
        summary = self._extract_optional_text(soup, source.article_summary_selector)
        content = self._extract_text(soup, source.article_content_selector) or ""
        published_at = self._parse_datetime(
            self._extract_optional_text(soup, source.article_published_at_selector)
        )
        tags = self._extract_tags(soup, source.article_tags_selector)

        raw_html_path = None
        if persist_raw:
            raw_html_path = self.file_store.save_raw_html(source.name, article_url, html)

        table_html = html
        if source.article_table_selector:
            selected_tables = soup.select(source.article_table_selector)
            if selected_tables:
                table_html = "\n".join(str(table) for table in selected_tables)

        table_result = extract_tables_from_html(
            html=table_html,
            source_name=source.name,
            article_title=title,
        )

        article = ArticleRecord(
            source_name=source.name,
            industry=source.industry,
            url=article_url,
            title=title,
            summary=summary,
            content=content,
            published_at=published_at,
            tags=tags,
            table_paths=table_result.table_paths,
            extracted_tables=table_result.tables,
            raw_html_path=raw_html_path,
            captured_at=datetime.utcnow(),
            content_hash=self._hash_text(f"{title}\n{content}"),
        )
        self.article_repository.save_article(article)
        return article

    @staticmethod
    def _extract_text(soup: BeautifulSoup, selector: str | None) -> str | None:
        if not selector:
            return None
        node = soup.select_one(selector)
        return node.get_text("\n", strip=True) if node else None

    def _extract_optional_text(self, soup: BeautifulSoup, selector: str | None) -> str | None:
        return self._extract_text(soup, selector)

    @staticmethod
    def _extract_tags(soup: BeautifulSoup, selector: str | None) -> list[str]:
        if not selector:
            return []
        return [node.get_text(strip=True) for node in soup.select(selector)]

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return date_parser.parse(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _hash_text(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()
