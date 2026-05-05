from pydantic import BaseModel, Field


class DailyReportRequest(BaseModel):
    report_date: str | None = None
    lookback_hours: int = Field(default=24, ge=1, le=168)
    top_k: int = Field(default=8, ge=3, le=20)


class DailyReportResponse(BaseModel):
    report_markdown: str
    citations: list[str]
    saved_path: str
