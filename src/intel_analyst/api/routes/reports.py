"""
日报生成接口。

POST /api/v1/reports/daily —— 根据时间段拉取文章，由 LLM 生成 structurized 日报
Markdown，保存到 data/reports/ 目录。被前端日报页使用。
"""

from fastapi import APIRouter, Depends

from intel_analyst.api.dependencies import get_report_service
from intel_analyst.schemas.report import DailyReportRequest, DailyReportResponse
from intel_analyst.services.report_service import ReportService

router = APIRouter()


@router.post("/daily", response_model=DailyReportResponse)
def generate_daily_report(
    payload: DailyReportRequest,
    report_service: ReportService = Depends(get_report_service),
) -> DailyReportResponse:
    return report_service.generate_daily_report(payload)
