"""
日报生成的请求/响应模型。

DailyReportRequest:  POST /reports/daily 的请求体，指定日期、回溯时间和文章数。
DailyReportResponse: 返回日报 Markdown、引用列表和保存路径。
"""

from pydantic import BaseModel, Field


class DailyReportRequest(BaseModel):
    report_date: str | None = None       # 日报日期（YYYY-MM-DD），默认今日
    lookback_hours: int = Field(default=24, ge=1, le=168)  # 回溯小时数，最长一周
    top_k: int = Field(default=8, ge=3, le=20)             # 用几篇文章生成日报


class DailyReportResponse(BaseModel):
    report_markdown: str
    citations: list[str]
    saved_path: str
