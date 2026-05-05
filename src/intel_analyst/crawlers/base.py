from abc import ABC, abstractmethod

from intel_analyst.schemas.article import ArticleRecord
from intel_analyst.schemas.source import SourceConfig


class BaseCrawler(ABC):
    @abstractmethod
    def crawl(
        self,
        source: SourceConfig,
        max_articles: int | None = None,
        persist_raw: bool = True,
    ) -> list[ArticleRecord]:
        raise NotImplementedError
