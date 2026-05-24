"""
健康检查接口。

GET /api/v1/health —— 返回服务状态、环境和向量库路径。
被前端健康检查轮询和运维监控使用。
"""

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
