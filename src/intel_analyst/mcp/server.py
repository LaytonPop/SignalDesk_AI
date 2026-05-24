"""
MCP 协议服务 —— 让 AI 助手（如 Claude Desktop）可以直接调用本项目的核心功能。

提供 3 个 tool 和 1 个 resource：
    - search_intelligence:   RAG 问答（等价于 POST /knowledge/query）
    - generate_daily_brief:  生成日报（等价于 POST /reports/daily）
    - crawl_and_ingest:      爬取并入库（等价于 POST /sources/crawl + auto_ingest）
    - brief://latest:        获取最新日报内容

启动命令：
    python -m intel_analyst.mcp.server

注意：这里每次调用都 new 了 Service（无缓存），因为 MCP 是长进程，
请求频率远低于 HTTP API，不需要单例优化。
"""

from mcp.server.fastmcp import FastMCP

from intel_analyst.core.config import get_settings
from intel_analyst.schemas.crawl import CrawlRequest
from intel_analyst.schemas.query import QueryRequest
from intel_analyst.schemas.report import DailyReportRequest
from intel_analyst.services.crawler_service import CrawlerService
from intel_analyst.services.query_service import QueryService
from intel_analyst.services.report_service import ReportService
from intel_analyst.storage.file_store import ensure_data_directories

settings = get_settings()
ensure_data_directories(settings)
mcp = FastMCP("industry-intelligence-analyst")


@mcp.tool()
def search_intelligence(question: str, top_k: int = 4) -> dict[str, object]:
    """行业情报 RAG 问答：基于知识库检索并生成答案。"""
    service = QueryService()
    result = service.query(QueryRequest(question=question, top_k=top_k))
    return result.model_dump()


@mcp.tool()
def generate_daily_brief(report_date: str | None = None, lookback_hours: int = 24) -> dict[str, object]:
    """生成日报：拉取最近文章，生成结构化日报。"""
    service = ReportService()
    result = service.generate_daily_report(
        DailyReportRequest(report_date=report_date, lookback_hours=lookback_hours)
    )
    return result.model_dump()


@mcp.tool()
def crawl_and_ingest(source_path: str, max_articles: int = 10) -> dict[str, object]:
    """爬取指定站点并自动入库到向量库。"""
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
    """返回最新日报的完整内容。"""
    report_files = sorted(settings.report_data_dir.glob("*.md"), key=lambda path: path.stat().st_mtime)
    if not report_files:
        return "暂无日报。"
    return report_files[-1].read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()
