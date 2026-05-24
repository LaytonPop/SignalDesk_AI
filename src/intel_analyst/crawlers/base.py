"""
爬虫基类 —— 定义爬虫的统一接口。

所有爬虫必须继承 BaseCrawler 并实现 crawl() 方法。
当前只有 GenericNewsCrawler 一个实现。
"""

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
