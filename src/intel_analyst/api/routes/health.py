from fastapi import APIRouter

from intel_analyst.core.config import get_settings

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "environment": settings.app_env,
        "vectorstore_dir": str(settings.vectorstore_dir),
    }
