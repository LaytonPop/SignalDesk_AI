from fastapi import APIRouter, Depends

from intel_analyst.api.dependencies import get_ingestion_service
from intel_analyst.services.ingestion_service import IngestionService
from intel_analyst.services.seed_service import SeedService

router = APIRouter()


@router.post("/rebuild-index")
def rebuild_index(
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> dict[str, int | str]:
    count = ingestion_service.rebuild_index()
    return {"status": "ok", "ingested_count": count}


@router.post("/seed")
def seed_sample_data() -> dict[str, int | str]:
    service = SeedService()
    count = service.seed()
    return {"status": "ok", "ingested_count": count}
