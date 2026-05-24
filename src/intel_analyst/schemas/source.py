"""
站点配置模型 —— 定义爬虫目标网站的结构。

SourceConfig: 描述一个新闻站点：URL、CSS 选择器（列表项、链接、标题、内容等）、
             爬取量限制、认证方式等。config/sources/ 目录下的 JSON 文件即为此模型。
AuthConfig:  站点的认证方式（无需认证 / requests 表单提交 / selenium 模拟登录）。

被以下模块使用：
    - CrawlerService.crawl() 接收 SourceConfig 作为爬取目标
    - SourceLoader.load() 从 JSON 文件反序列化为 SourceConfig
    - GenericNewsCrawler.crawl() 根据配置执行爬取
"""

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class AuthConfig(BaseModel):
    mode: Literal["none", "requests", "selenium"] = "none"
    login_url: HttpUrl | None = None
    username_env: str | None = None       # 用户名所在的环境变量名
    password_env: str | None = None       # 密码所在的环境变量名
    username_selector: str | None = None  # 用户名输入框的 CSS 选择器
    password_selector: str | None = None  # 密码输入框的 CSS 选择器
    submit_selector: str | None = None    # 提交按钮的 CSS 选择器
    success_selector: str | None = None   # 登录成功后的标识元素 CSS 选择器
    timeout_seconds: int = 20


class SourceConfig(BaseModel):
    name: str
    industry: str | None = None
    base_url: HttpUrl
    list_url: HttpUrl                         # 文章列表页 URL
    list_item_selector: str                   # 列表项 CSS 选择器
    article_link_selector: str                # 文章链接 CSS 选择器（在列表项内）
    article_title_selector: str               # 文章标题 CSS 选择器
    article_content_selector: str             # 文章正文 CSS 选择器
    article_summary_selector: str | None = None      # 文章摘要 CSS 选择器（可选）
    article_published_at_selector: str | None = None  # 发布时间 CSS 选择器（可选）
    article_tags_selector: str | None = None          # 标签 CSS 选择器（可选）
    article_table_selector: str | None = None         # 表格 CSS 选择器（可选）
    list_published_at_selector: str | None = None     # 列表页时间 CSS 选择器（可选）
    max_articles: int = Field(default=20, ge=1, le=100)
    default_headers: dict[str, str] = Field(default_factory=dict)
    auth: AuthConfig = Field(default_factory=AuthConfig)
