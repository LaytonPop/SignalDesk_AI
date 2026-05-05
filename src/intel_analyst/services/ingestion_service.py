from langchain_core.documents import Document

from intel_analyst.schemas.article import ArticleRecord
from intel_analyst.storage.article_repository import ArticleRepository
from intel_analyst.rag.vector_store import VectorStoreManager


class IngestionService:
    def __init__(self) -> None:
        self.vector_store = VectorStoreManager()
        self.repository = ArticleRepository()

    def ingest_articles(self, articles: list[ArticleRecord]) -> int:
        documents = [self._to_document(article) for article in articles]
        return self.vector_store.add_documents(documents)

    def rebuild_index(self) -> int:
        articles = self.repository.iter_articles()
        self.vector_store.reset_collection()
        return self.ingest_articles(articles)

    @staticmethod
    def _to_document(article: ArticleRecord) -> Document:
        table_context = "\n".join(
            [
                f"表格{table.index}: 行数={table.row_count}, 列数={table.column_count}, 预览={table.json_preview}"
                for table in article.extracted_tables
            ]
        )
        content = (
            f"标题: {article.title}\n"
            f"摘要: {article.summary or ''}\n"
            f"正文: {article.content}\n"
            f"表格信息: {table_context}"
        )
        metadata = {
            "title": article.title,
            "url": str(article.url),
            "source_name": article.source_name,
            "industry": article.industry or "",
            "published_at": article.published_at.isoformat() if article.published_at else "",
            "tags": ",".join(article.tags),
        }
        return Document(page_content=content, metadata=metadata)
