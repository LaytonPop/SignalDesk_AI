from datetime import datetime

from intel_analyst.schemas.article import ArticleRecord
from intel_analyst.storage.article_repository import ArticleRepository


def test_save_and_list_articles():
    repo = ArticleRepository()
    article = ArticleRecord(
        source_name="demo",
        industry="AI",
        url="https://example.com/article-1",
        title="Test Article",
        summary="Summary",
        content="Content",
        published_at=datetime.utcnow(),
        tags=["tag1"],
        captured_at=datetime.utcnow(),
        content_hash="repo_test_hash",
    )
    repo.save_article(article)
    items = repo.list_articles(limit=10)
    assert any(item.content_hash == "repo_test_hash" for item in items)
