# Phase 2：采集与结构化层

## 这一阶段你要做出什么

完成后，你要能把一个行业资讯站点的数据抓下来，并整理成结构化文件。

具体结果应该包括：

- 原始 HTML
- 清洗后的文章 JSON
- 从 HTML 表格导出的 CSV

## 这一阶段为什么关键

RAG 的上限，很大程度取决于你的数据质量。抓得不完整、表格没抽干净、元数据没有保留，后面问答效果通常都会差。

## 这一阶段涉及的文件

- `config/sources/sample_industry_site.json`
- `src/intel_analyst/schemas/source.py`
- `src/intel_analyst/schemas/article.py`
- `src/intel_analyst/crawlers/source_loader.py`
- `src/intel_analyst/crawlers/auth.py`
- `src/intel_analyst/crawlers/base.py`
- `src/intel_analyst/crawlers/generic_news.py`
- `src/intel_analyst/processing/html_tables.py`
- `src/intel_analyst/storage/article_repository.py`

## 手把手实现顺序

### Step 1：先设计站点配置格式

你要做的事：

- 把“一个站点需要哪些信息才能被抓取”列清楚
- 用 `SourceConfig` 和 `AuthConfig` 做成 Pydantic Schema

最低要包括：

- 列表页 URL
- 列表 item selector
- 详情页链接 selector
- 标题 / 正文 / 时间 / 标签 selector
- 表格 selector
- 登录模式

你现在的代码对应位置：

- `src/intel_analyst/schemas/source.py`
- `config/sources/sample_industry_site.json`

验收：

- 一个 JSON 配置文件可以被成功解析成 `SourceConfig`

### Step 2：建立配置加载器

你要做的事：

- 从 `config/sources/` 读取 JSON
- 把相对路径统一转成项目根目录下的绝对路径

你现在的代码对应位置：

- `src/intel_analyst/crawlers/source_loader.py`

验收：

- 给一个配置路径，程序能返回合法的 `SourceConfig`

### Step 3：先做 requests 登录和抓取

你要做的事：

- 封装 `requests.Session`
- 如果站点是表单登录，先请求登录页，再提交账号密码
- 登录成功后继续抓列表页和详情页

你现在的代码对应位置：

- `src/intel_analyst/crawlers/auth.py`
- `src/intel_analyst/crawlers/generic_news.py`

重点理解：

- 为什么用 `Session` 保存 Cookie
- 为什么登录逻辑要和抓取逻辑分开

### Step 4：补 Selenium 登录兜底

你要做的事：

- 对需要 JS 渲染或交互登录的站点，使用 Selenium 模拟登录
- 登录成功后把 Cookie 同步回 `requests.Session`

你现在的代码对应位置：

- `src/intel_analyst/crawlers/auth.py`

重点理解：

- Selenium 不是默认方案，而是为复杂登录做兜底
- 抓正文时依然尽量回到 `requests`，速度更快、更稳定

### Step 5：解析文章正文和元数据

你要做的事：

- 用 `BeautifulSoup` 提取标题、摘要、正文、时间、标签
- 生成 `ArticleRecord`
- 给每篇文章计算 `content_hash`

你现在的代码对应位置：

- `src/intel_analyst/schemas/article.py`
- `src/intel_analyst/crawlers/generic_news.py`

验收：

- 能得到结构完整的文章对象，而不是只抓到一段正文

### Step 6：把 HTML 表格转成结构化数据

你要做的事：

- 用 `Pandas.read_html()` 抽表格
- 导出为 CSV
- 保存一个 JSON 预览用于调试或后续前端展示

你现在的代码对应位置：

- `src/intel_analyst/processing/html_tables.py`

重点理解：

- 为什么先限制到文章里的表格 selector 再交给 Pandas
- 为什么不仅保存 CSV，还保存预览数据和行列数

验收：

- 对带表格的文章，`data/tables/` 下能生成 CSV

### Step 7：把文章和原始内容落盘

你要做的事：

- 把原始 HTML 写入 `data/raw`
- 把结构化文章 JSON 写入 `data/processed`

你现在的代码对应位置：

- `src/intel_analyst/storage/file_store.py`
- `src/intel_analyst/storage/article_repository.py`

验收：

- 抓完一次后，三个目录里都有对应产物

## 阶段验收清单

- 能加载站点配置
- 能抓到列表页和详情页
- 能解析文章基本字段
- 能抽取表格并生成 CSV
- 能把原始和结构化数据落盘

## 常见坑

- selector 写对了列表页，却没对详情页逐篇验证
- Selenium 登录成功了，但 Cookie 没同步给 Session
- `read_html()` 直接喂整页 HTML，抽到了无关表格
- 发布时间没统一解析，后面日报筛选会乱
