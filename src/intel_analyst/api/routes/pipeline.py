"""
数据管道接口（管理/运维用）。

POST /api/v1/pipeline/rebuild-index —— 清空向量库，从所有已处理文章中重新构建索引。
POST /api/v1/pipeline/seed —— 向量库中注入示例文章数据，用于测试（爬虫未就绪时的替代方案）。
"""

from fastapi import APIRouter, Depends

from intel_analyst.api.dependencies import get_ingestion_service
from intel_analyst.services.ingestion_service import IngestionService
from intel_analyst.services.seed_service import SeedService

router = APIRouter()


@router.post("/rebuild-index")
def rebuild_index(ingestion_service: IngestionService = Depends(get_ingestion_service),) -> dict[str, int | str]:
    count = ingestion_service.rebuild_index()
    return {"status": "ok", "ingested_count": count}


@router.post("/seed")
def seed_sample_data() -> dict[str, int | str]:
    service = SeedService()
    count = service.seed()
    return {"status": "ok", "ingested_count": count}
