from datetime import datetime, timedelta

from langchain_core.output_parsers import StrOutputParser

from intel_analyst.core.config import get_settings
from intel_analyst.rag.llm import build_chat_model
from intel_analyst.rag.prompts import build_daily_report_prompt
from intel_analyst.schemas.report import DailyReportRequest, DailyReportResponse
from intel_analyst.storage.article_repository import ArticleRepository
from intel_analyst.storage.file_store import FileStore


class ReportService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.repository = ArticleRepository()
        self.file_store = FileStore()
        self.llm = build_chat_model()
        self.prompt = build_daily_report_prompt()
        self.parser = StrOutputParser()

    def generate_daily_report(self, payload: DailyReportRequest) -> DailyReportResponse:
        cutoff = datetime.utcnow() - timedelta(hours=payload.lookback_hours)
        articles = [
            article
            for article in self.repository.iter_articles()
            if article.published_at is None or article.published_at >= cutoff
        ]
        selected = articles[: payload.top_k]
        context = "\n\n".join(
            [
                (
                    f"标题: {article.title}\n"
                    f"时间: {article.published_at.isoformat() if article.published_at else 'unknown'}\n"
                    f"来源: {article.source_name}\n"
                    f"摘要: {article.summary or ''}\n"
                    f"正文节选: {article.content[:800]}"
                )
                for article in selected
            ]
        )
        chain = self.prompt | self.llm | self.parser
        report_markdown = chain.invoke({"context": context or "暂无资讯可生成日报。"})

        report_date = payload.report_date or datetime.utcnow().strftime("%Y-%m-%d")
        filename = f"daily_report_{report_date}.md"
        saved_path = self.file_store.save_json(
            directory=self.settings.report_data_dir,
            filename=filename,
            content=report_markdown,
        )
        citations = [f"{article.title} | {article.source_name}" for article in selected]
        return DailyReportResponse(
            report_markdown=report_markdown,
            citations=citations,
            saved_path=saved_path,
        )
