"""
文章入库服务 —— 将 ArticleRecord 列表转换为向量库中的可检索文档。

职责：
    1. _to_document(): 把 ArticleRecord 转为 LangChain Document（含格式化文本 + 元数据），
       每个 Document 对应向量库中的一个可检索条目
    2. ingest_articles(): 批量切片后写入 Chroma 向量库
    3. rebuild_index(): 清空向量库，从所有已处理文章中重新构建（全量重建）

被以下模块调用：
    - CrawlerService.crawl() —— 爬取完文章后自动入库
    - POST /pipeline/rebuild-index —— 全量重建索引
    - SeedService.seed() —— 注入示例数据
"""

from langchain_core.documents import Document

from intel_analyst.schemas.article import ArticleRecord
from intel_analyst.storage.article_repository import ArticleRepository
from intel_analyst.rag.vector_store import VectorStoreManager


class IngestionService:
    def __init__(self) -> None:
        self.vector_store = VectorStoreManager()
        self.repository = ArticleRepository()

    def ingest_articles(self, articles: list[ArticleRecord]) -> int:
        """将文章列表转为文档后写入向量库，返回实际写入的切片数量。"""
        documents = [self._to_document(article) for article in articles]
        return self.vector_store.add_documents(documents)

    def rebuild_index(self) -> int:
        """清空向量库，重新从 ArticleRepository 读取所有文章并入库。"""
        articles = self.repository.iter_articles()
        self.vector_store.reset_collection()
        return self.ingest_articles(articles)

    @staticmethod
    def _to_document(article: ArticleRecord) -> Document:
        """将 ArticleRecord 转为 LangChain Document。

        格式化的文本内容包含：标题、摘要、正文、表格信息。
        元数据包含：标题、URL、来源、行业、发布时间、标签。
        """
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
