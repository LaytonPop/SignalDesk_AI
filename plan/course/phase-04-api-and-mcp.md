# Phase 4：接口与协作层

## 这一阶段你要做出什么

这一阶段的目标，是把前面做好的抓取、RAG、日报能力开放出来，让它变成真正的服务。

完成后，你要有：

- RESTful API
- 请求与响应 Schema
- 简单错误处理
- MCP tools
- MCP resource

## 这一阶段涉及的文件

- `src/intel_analyst/schemas/crawl.py`
- `src/intel_analyst/schemas/query.py`
- `src/intel_analyst/schemas/report.py`
- `src/intel_analyst/api/dependencies.py`
- `src/intel_analyst/api/router.py`
- `src/intel_analyst/api/routes/health.py`
- `src/intel_analyst/api/routes/sources.py`
- `src/intel_analyst/api/routes/articles.py`
- `src/intel_analyst/api/routes/knowledge.py`
- `src/intel_analyst/api/routes/reports.py`
- `src/intel_analyst/api/routes/pipeline.py`
- `src/intel_analyst/mcp/server.py`

## 手把手实现顺序

### Step 1：先定义请求与响应对象

你要做的事：

- 给抓取、问答、日报定义明确的 Schema
- 不要在路由里直接收裸字典

你现在的代码对应位置：

- `src/intel_analyst/schemas/crawl.py`
- `src/intel_analyst/schemas/query.py`
- `src/intel_analyst/schemas/report.py`

### Step 2：写 Service 依赖注入层

你要做的事：

- 统一在 `api/dependencies.py` 实例化服务
- 保持路由轻量

你现在的代码对应位置：

- `src/intel_analyst/api/dependencies.py`

### Step 3：建立 API 路由

你要做的事：

- `/health`
- `/sources/crawl`
- `/articles`
- `/knowledge/query`
- `/reports/daily`
- `/pipeline/rebuild-index`

你现在的代码对应位置：

- `src/intel_analyst/api/router.py`
- `src/intel_analyst/api/routes/*.py`

重点理解：

- 路由层只接参数和回结果
- 真正业务逻辑留在 `services/`

### Step 4：补基础异常处理

你要做的事：

- 对参数缺失、配置缺失、抓取失败给出合理报错
- 至少先处理 `400` 级别常见输入问题

你现在的代码对应位置：

- `src/intel_analyst/api/routes/sources.py`

### Step 5：把能力封装成 MCP 工具

你要做的事：

- 封装 `search_intelligence`
- 封装 `generate_daily_brief`
- 封装 `crawl_and_ingest`
- 提供 `brief://latest` 资源

你现在的代码对应位置：

- `src/intel_analyst/mcp/server.py`

重点理解：

- MCP 让你的项目能被外部 Agent 直接调用
- 这是比“只做 API”更有时代感的亮点

## 阶段验收清单

- 可以通过 HTTP 触发抓取
- 可以通过 HTTP 做问答
- 可以通过 HTTP 生成日报
- MCP server 可以启动
- MCP tool 能返回结构化结果

## 常见坑

- 路由里直接写业务逻辑，后面越来越难测
- API 能返回答案，但没返回 citation
- MCP 工具和 HTTP 接口各写一套逻辑，造成重复
