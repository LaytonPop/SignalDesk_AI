import os

# Must be set before any HuggingFace imports to use mirror in China
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

from contextlib import asynccontextmanager

from fastapi import FastAPI

from intel_analyst.api.router import api_router
from intel_analyst.core.config import get_settings
from intel_analyst.core.logging import configure_logging
from intel_analyst.storage.file_store import ensure_data_directories


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    configure_logging(settings.app_env)
    ensure_data_directories(settings)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Smart Industry Intelligence Analyst",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
