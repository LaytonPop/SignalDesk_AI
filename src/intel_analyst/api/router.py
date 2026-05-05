from fastapi import APIRouter

from intel_analyst.api.routes import articles, health, knowledge, pipeline, reports, sources

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(articles.router, tags=["articles"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])
