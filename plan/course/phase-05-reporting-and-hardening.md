# Phase 5：日报与工程增强层

## 这一阶段你要做出什么

这一阶段不只是“再加一个功能”，而是让项目更接近一个能演示、能讲述、能继续扩展的完整应用。

完成后，你应该具备：

- 行业日报生成能力
- 基础测试
- 更好的日志与错误定位能力
- 更清晰的后续扩展路线

## 这一阶段涉及的文件

- `src/intel_analyst/services/report_service.py`
- `tests/test_html_tables.py`
- `tests/test_article_repository.py`
- `tests/test_health_api.py`
- `README.md`
- `config/sources/`

## 手把手实现顺序

### Step 1：先做日报生成服务

你要做的事：

- 读取最近一段时间的文章
- 拼成日报上下文
- 调用 LLM 生成 Markdown 报告
- 存储到 `data/reports/`

你现在的代码对应位置：

- `src/intel_analyst/services/report_service.py`

重点理解：

- 日报不是普通摘要，应该面向职场场景输出“重点、影响、风险、建议动作”

### Step 2：补最基础的测试

你要做的事：

- 先写能快速跑起来的单元测试
- 优先覆盖：健康检查、表格结构化、文章仓储

你现在的代码对应位置：

- `tests/test_health_api.py`
- `tests/test_html_tables.py`
- `tests/test_article_repository.py`

验收：

- 依赖安装后，`pytest` 至少能跑过这些基础用例

### Step 3：整理 README 和启动方式

你要做的事：

- 写清楚依赖安装
- 写清楚 `.env` 配置
- 写清楚 FastAPI 和 MCP 的启动命令

你现在的代码对应位置：

- `README.md`
- `.env.example`

### Step 4：为真实站点适配做准备

你要做的事：

- 在 `config/sources/` 下新增真实站点配置
- 一个字段一个字段验证 selector
- 记录哪些页面必须登录、哪些可以匿名抓

建议做法：

- 先找一个公开可访问的行业资讯站练手
- 先只抓列表页前 5 篇，调通后再放大

### Step 5：思考下一轮扩展

下一步可以继续做：

- 增量抓取，避免重复入库
- 多站点聚合
- APScheduler 定时抓取与日报生成
- 企业微信 / 飞书推送
- 一个简单前端工作台

## 阶段验收清单

- 日报可以生成并落盘
- 基础测试可运行
- 项目启动说明清晰
- 至少准备好一个真实站点配置方向

## 常见坑

- 日报上下文拼得太长，模型响应慢或成本高
- 测试依赖真实网络，导致不稳定
- README 只写了功能，没写如何复现
