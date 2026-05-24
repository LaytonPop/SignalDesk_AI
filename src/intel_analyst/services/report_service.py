"""
日报生成服务 —— 从已处理文章中拉取最近文章，由 LLM 生成结构化日报。

流程：
    1. 根据 lookback_hours 筛选文章
    2. 取前 top_k 篇，拼接内容为上下文
    3. LLM 生成 Markdown 格式日报（含今日重点、业务影响、风险提示、建议动作）
    4. 保存到 data/reports/daily_report_{date}.md
    5. 返回日报 Markdown + 引用 + 文件路径

被 POST /api/v1/reports/daily 调用。
也被 mcp/server.py 的 generate_daily_brief tool 调用。
"""

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
        # Step 1: 按时间段筛选文章
        cutoff = datetime.utcnow() - timedelta(hours=payload.lookback_hours)
        articles = [
            article
            for article in self.repository.iter_articles()
            if article.published_at is None or article.published_at >= cutoff
        ]
        selected = articles[: payload.top_k]

        # Step 2: 拼接上下文
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

        # Step 3: LLM 生成日报
        chain = self.prompt | self.llm | self.parser
        report_markdown = chain.invoke({"context": context or "暂无资讯可生成日报。"})

        # Step 4: 保存日报文件
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
