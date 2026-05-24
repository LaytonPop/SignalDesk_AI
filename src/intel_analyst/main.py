"""
FastAPI 应用入口。

启动命令：
    uvicorn intel_analyst.main:app --reload --app-dir src

app = create_app() 是 uvicorn 直接 import 的模块级实例。
"""

import os

# 必须在任何 HuggingFace 相关 import 之前执行：
# 模型下载后走本地缓存，避免每次启动尝试联网
os.environ.setdefault("HF_HUB_OFFLINE", "1")

from contextlib import asynccontextmanager

from fastapi import FastAPI

from intel_analyst.api.router import api_router
from intel_analyst.core.config import get_settings
from intel_analyst.core.logging import configure_logging
from intel_analyst.storage.file_store import ensure_data_directories


@asynccontextmanager
async def lifespan(_: FastAPI):
    """应用启动时初始化日志和数据目录，关闭时不执行任何操作。"""
    settings = get_settings()
    configure_logging(settings.app_env)
    ensure_data_directories(settings)
    yield


def create_app() -> FastAPI:
    """工厂函数：创建 FastAPI 实例，挂载 /api/v1 路由。"""
    settings = get_settings()
    app = FastAPI(
        title="Smart Industry Intelligence Analyst",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
