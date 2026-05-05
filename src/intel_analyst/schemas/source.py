from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class AuthConfig(BaseModel):
    mode: Literal["none", "requests", "selenium"] = "none"
    login_url: HttpUrl | None = None
    username_env: str | None = None
    password_env: str | None = None
    username_selector: str | None = None
    password_selector: str | None = None
    submit_selector: str | None = None
    success_selector: str | None = None
    timeout_seconds: int = 20


class SourceConfig(BaseModel):
    name: str
    industry: str | None = None
    base_url: HttpUrl
    list_url: HttpUrl
    list_item_selector: str
    article_link_selector: str
    article_title_selector: str
    article_content_selector: str
    article_summary_selector: str | None = None
    article_published_at_selector: str | None = None
    article_tags_selector: str | None = None
    article_table_selector: str | None = None
    list_published_at_selector: str | None = None
    max_articles: int = Field(default=20, ge=1, le=100)
    default_headers: dict[str, str] = Field(default_factory=dict)
    auth: AuthConfig = Field(default_factory=AuthConfig)
