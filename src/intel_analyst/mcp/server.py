from mcp.server.fastmcp import FastMCP

from intel_analyst.schemas.crawl import CrawlRequest
from intel_analyst.schemas.query import QueryRequest
from intel_analyst.schemas.report import DailyReportRequest
from intel_analyst.services.crawler_service import CrawlerService
from intel_analyst.services.query_service import QueryService
from intel_analyst.services.report_service import ReportService
from intel_analyst.storage.file_store import ensure_data_directories
from intel_analyst.core.config import get_settings


settings = get_settings()
ensure_data_directories(settings)
mcp = FastMCP("industry-intelligence-analyst")


@mcp.tool()
def search_intelligence(question: str, top_k: int = 4) -> dict[str, object]:
    service = QueryService()
    result = service.query(QueryRequest(question=question, top_k=top_k))
    return result.model_dump()


@mcp.tool()
def generate_daily_brief(report_date: str | None = None, lookback_hours: int = 24) -> dict[str, object]:
    service = ReportService()
    result = service.generate_daily_report(
        DailyReportRequest(report_date=report_date, lookback_hours=lookback_hours)
    )
    return result.model_dump()


@mcp.tool()
def crawl_and_ingest(source_path: str, max_articles: int = 10) -> dict[str, object]:
    service = CrawlerService()
    result = service.crawl(
        CrawlRequest(
            source_path=source_path,
            max_articles=max_articles,
            persist_raw=True,
            auto_ingest=True,
        )
    )
    return result.model_dump()


@mcp.resource("brief://latest")
def latest_brief() -> str:
    report_files = sorted(settings.report_data_dir.glob("*.md"), key=lambda path: path.stat().st_mtime)
    if not report_files:
        return "暂无日报。"
    return report_files[-1].read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()
