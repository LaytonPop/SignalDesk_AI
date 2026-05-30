# SignalDesk AI — Agent 操作指令

## 角色

你正在协助 **SignalDesk AI** 代码库，一个智能行业情报分析平台。你用 Python（后端）和 TypeScript/React（前端）编写代码。遵循以下约定。

## 关键环境规则

- **Python 环境**：必须使用 conda 环境：`C:/Users/morganWen/.conda/envs/singnalDesk/python.exe`。系统默认 `python` 指向 Anaconda3，用它启动会失败。
- **HF 模型**：`main.py` 顶部设置了 `HF_HUB_OFFLINE=1`，模型必须提前下载到 `~/.cache/huggingface/hub/`。不要用 `hf-mirror.com`——huggingface.co 可直连。
- **DeepSeek API**：只支持 chat/completion，不支持 embedding。embedding 必须走本地 HF 模型（`BAAI/bge-small-zh-v1.5`）。
- **环境文件**：后端用 `.env`（项目根目录）；前端用 `web/.env.local`。两者独立。

## 启动方式

```bash
# 后端（项目根目录）
& "C:/Users/morganWen/.conda/envs/singnalDesk/python.exe" -m uvicorn intel_analyst.main:app --reload --app-dir src --host 127.0.0.1 --port 8000

# 前端
cd web && npm run dev

# MCP Server（可选）
python -m intel_analyst.mcp.server

# 测试
python -m pytest tests/ -v
```

## 架构规范

### 分层（严格遵循，不可违反）

```
api/routes/     →  仅 HTTP 层：校验参数、调用 service、返回响应
services/       →  业务编排：可以使用 crawlers/processing/rag/storage
crawlers/       →  爬虫逻辑：禁止依赖 api/ 或 services/
rag/            →  embedding、向量库、LLM、prompt：不感知 HTTP
storage/        →  文件读写与仓储：不含业务逻辑
schemas/        →  仅 Pydantic 模型：无逻辑、不 import 其他模块
mcp/            →  MCP Server：将 service 封装为 AI Agent 可调用的工具
```

### 依赖注入

`api/dependencies.py` 中所有 getter 均使用 `@lru_cache(maxsize=1)` 实现单例。路由中一律通过 `Depends(get_xxx_service)` 注入，**禁止**在路由函数体内 `new` 一个 service。

**例外**：`pipeline.py` 的 `seed_sample_data()` 目前违反此规则，直接在函数体内调用了 `SeedService()`。修改该文件时一并修掉。

### 响应模型

所有路由处理函数**必须**使用 Pydantic `response_model`。当前唯一违反者是 `pipeline.py`（返回裸 `dict`）。修改该文件时一并修掉。

## 代码约定

- **Import**：使用从 `intel_analyst.*` 开始的绝对导入。例如：`from intel_analyst.core.config import get_settings`
- **时间处理**：使用 `datetime.now(timezone.utc)`，**禁止**使用已废弃的 `datetime.utcnow()`。`report_service.py` 仍在使用旧写法——发现即修。
- **配置读取**：始终使用 `get_settings()` 单例，禁止直接读环境变量。
- **文件命名**：Python 模块用 `snake_case`。TypeScript 文件用 `kebab-case` 或 Next.js 惯例。
- **行宽**：Python 文件 Ruff 配置为 100 字符。

## 测试

- 框架：pytest（含 pytest-asyncio）
- 测试客户端使用 `create_app()` 工厂函数，而非模块级 `app` 实例
- 运行：`python -m pytest tests/ -v`
- 测试文件放在 `tests/` 目录，以 `test_` 前缀命名

## 核心文件速查

| 文件 | 用途 |
|------|------|
| `src/intel_analyst/main.py` | FastAPI app 工厂 + lifespan |
| `src/intel_analyst/core/config.py` | 全部配置（来自 `.env`） |
| `src/intel_analyst/api/dependencies.py` | Service 单例 getter |
| `src/intel_analyst/api/router.py` | 路由注册中心 |
| `src/intel_analyst/rag/vector_store.py` | Chroma 封装 |
| `src/intel_analyst/rag/llm.py` | LLM 工厂（DeepSeek/Ollama） |
| `src/intel_analyst/rag/embeddings.py` | Embedding 工厂（HF/OpenAI） |
| `src/intel_analyst/mcp/server.py` | MCP 工具定义 |
| `web/lib/backend.ts` | Next.js → FastAPI 代理辅助函数 |
| `web/components/intelligence-workbench.tsx` | 前端主组件 |

## Git 工作流（Conventional Commits + Feature Branch）

### Commit 信息格式

```
<type>(<scope>): <subject>
```

| type | 使用场景 |
|------|----------|
| `feat` | 新功能 |
| `fix` | 修 bug |
| `docs` | 仅文档变更 |
| `chore` | 清理、依赖、构建、gitignore |
| `refactor` | 重构（不改行为） |
| `test` | 新增或修改测试 |
| `style` | 格式化、空格（无逻辑变化） |

### 分支命名

```
<type>/<简短描述>
```

示例：`feat/hybrid-retrieval`、`fix/crawler-retry`、`docs/readme-architecture`

### 硬规则

1. **禁止直推 `main`。** 始终先建分支：
   ```bash
   git checkout -b feat/xxx
   ```
2. **一个分支 = 一个逻辑完整的工作单元。** 分支可以包含多个 commit，但必须能用一句话概括。不要把修 bug 和加新功能混在同一个分支里。
3. **每完成一个有意义的步骤就 commit**，不要攒到最后一次提交。一个分支通常有 3~5 个 commit 展示推进过程。
4. **推送分支后通过 PR 合并**到 main。即使是单人项目，养成这个习惯能留下干净的提交历史，面试时也能展示。

### 合并后清理

```bash
git checkout main
git pull origin main
git branch -d feat/xxx   # 删除本地分支
```

## 常见陷阱

1. **不要在 `main.py` 运行之前 import HuggingFace**——`HF_HUB_OFFLINE` 必须先设置。
2. **不要无确认地调用 `reset_collection()`**——它会立即清空向量库。
3. **不要用 `datetime.utcnow()`**——已废弃，用 `datetime.now(timezone.utc)`。
4. **不要在 `api/routes/` 中写业务逻辑**——路由只是薄薄一层。
5. **不要从路由返回裸 `dict`**——始终使用 Pydantic response_model。
6. 前端不直连后端——所有请求通过 `web/app/api/*/route.ts` 代理转发。
