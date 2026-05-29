# SignalDesk AI — Agent Instructions

## Role

You are assisting with the **SignalDesk AI** codebase — a Smart Industry Intelligence Analyst platform. You write Python (backend) and TypeScript/React (frontend). Follow the conventions below.

## Critical Environment Rules

- **Python**: Always use the conda env: `C:/Users/morganWen/.conda/envs/singnalDesk/python.exe`. The system `python` points to Anaconda3 and will fail.
- **HF Models**: `main.py` sets `HF_HUB_OFFLINE=1` at import time. Models must be pre-downloaded to `~/.cache/huggingface/hub/`. Do NOT use `hf-mirror.com` — huggingface.co is directly accessible.
- **DeepSeek API**: Supports chat/completion only — does NOT support embedding. Embedding MUST use local HF model (`BAAI/bge-small-zh-v1.5`).
- **Environment files**: Backend uses `.env` (root); frontend uses `web/.env.local`. They are separate.

## How to Run

```bash
# Backend (from project root)
& "C:/Users/morganWen/.conda/envs/singnalDesk/python.exe" -m uvicorn intel_analyst.main:app --reload --app-dir src --host 127.0.0.1 --port 8000

# Frontend
cd web && npm run dev

# MCP Server (optional)
python -m intel_analyst.mcp.server

# Tests
python -m pytest tests/ -v
```

## Architecture Rules

### Layering (strict — do not violate)

```
api/routes/     →  HTTP layer only: validate params, call service, return response
services/       →  business orchestration: can use crawlers/processing/rag/storage
crawlers/       →  scraping logic: NO dependency on api/ or services/
rag/            →  embeddings, vector store, LLM, prompts: NO HTTP awareness
storage/        →  file I/O and repository: NO business logic
schemas/        →  Pydantic models only: NO logic, NO imports from other modules
mcp/            →  MCP Server: wraps services as tools for AI agents
```

### Dependency Injection

All service getters in `api/dependencies.py` use `@lru_cache(maxsize=1)` for singleton behavior. Always inject via `Depends(get_xxx_service)` in route handlers — never `new` a service in a route body.

**Exception**: `pipeline.py` `seed_sample_data()` currently violates this by calling `SeedService()` directly. When touching that file, fix to use DI.

### Response Models

All route handlers MUST use Pydantic `response_model`. The only current violator is `pipeline.py` (returns bare `dict`). Fix when touching that file.

## Code Conventions

- **Imports**: Use absolute imports from `intel_analyst.*`. Example: `from intel_analyst.core.config import get_settings`
- **Datetime**: Use `datetime.now(timezone.utc)`, NOT the deprecated `datetime.utcnow()`. `report_service.py` still uses the old form — fix on sight.
- **Configuration**: Always use `get_settings()` singleton. Never read env vars directly.
- **File naming**: Python modules use `snake_case`. TypeScript files use `kebab-case` or conventional Next.js patterns.
- **Line length**: Ruff configured at 100 chars for Python.

## Testing

- Framework: pytest (with pytest-asyncio)
- Test client uses `create_app()` factory (not the module-level `app`)
- Run: `python -m pytest tests/ -v`
- Tests should be in `tests/` with `test_` prefix

## Key Files to Know

| File | Purpose |
|------|---------|
| `src/intel_analyst/main.py` | FastAPI app factory + lifespan |
| `src/intel_analyst/core/config.py` | All settings from `.env` |
| `src/intel_analyst/api/dependencies.py` | Service singletons |
| `src/intel_analyst/api/router.py` | Route registration hub |
| `src/intel_analyst/rag/vector_store.py` | Chroma wrapper |
| `src/intel_analyst/rag/llm.py` | LLM factory (DeepSeek/Ollama) |
| `src/intel_analyst/rag/embeddings.py` | Embedding factory (HF/OpenAI) |
| `src/intel_analyst/mcp/server.py` | MCP tool definitions |
| `web/lib/backend.ts` | Next.js → FastAPI proxy helper |
| `web/components/intelligence-workbench.tsx` | Main UI component |

## Common Pitfalls

1. **Do NOT** import HuggingFace before `main.py` runs — `HF_HUB_OFFLINE` must be set first.
2. **Do NOT** call `reset_collection()` without confirmation — it wipes the vector DB immediately.
3. **Do NOT** use `datetime.utcnow()` — it's deprecated; use `datetime.now(timezone.utc)`.
4. **Do NOT** add business logic to `api/routes/` — routes are thin wrappers.
5. **Do NOT** return bare `dict` from routes — always use a Pydantic response model.
6. The frontend does NOT call the backend directly — it goes through `web/app/api/*/route.ts` proxy routes.
