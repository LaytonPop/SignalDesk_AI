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
