"""
全项目唯一的配置中心。

Settings 类从 .env 文件读取所有配置项，其他模块通过 get_settings()
获取同一个缓存的 Settings 实例。被 main.py、所有 service、所有 storage、
所有 rag 模块、所有 crawler 等几乎全部模块引用。

数据目录结构（启动时由 ensure_data_directories 自动创建）：
    data/
    ├── raw/         爬虫爬取的原始 HTML
    ├── processed/   清洗后的结构化 JSON（按 source_name 分子目录）
    ├── tables/      HTML 表格导出的 CSV
    ├── reports/     生成的日报 Markdown
    └── vectorstore/ Chroma 向量库持久化目录

环境变量前缀：INTEL_ANALYST_（在 .env 中定义，pydantic-settings 自动匹配）
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",           # 从项目根目录的 .env 加载
        env_prefix="INTEL_ANALYST_",  # 环境变量需带此前缀，如 INTEL_ANALYST_LLM_PROVIDER
        extra="ignore",            # .env 中无关的变量不报错
    )

    # ---- 运行模式 ----
    app_env: str = "dev"
    api_v1_prefix: str = "/api/v1"

    # ---- 目录路径（基于 ROOT_DIR） ----
    root_dir: Path = ROOT_DIR
    config_dir: Path = ROOT_DIR / "config"
    data_dir: Path = ROOT_DIR / "data"
    raw_data_dir: Path = ROOT_DIR / "data" / "raw"
    processed_data_dir: Path = ROOT_DIR / "data" / "processed"
    table_data_dir: Path = ROOT_DIR / "data" / "tables"
    report_data_dir: Path = ROOT_DIR / "data" / "reports"
    vectorstore_dir: Path = ROOT_DIR / "data" / "vectorstore"

    # ---- LLM 配置（回答生成） ----
    llm_provider: str = "ollama"         # "openai" 走 DeepSeek/OpenAI 兼容 API，或 "ollama" 走本地
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    openai_base_url: str | None = None   # DeepSeek API 地址
    openai_api_key: str | None = None    # DeepSeek API 密钥
    openai_model: str | None = None      # 如 deepseek-v4-flash

    # ---- Embedding 配置（向量化，用于 RAG 检索） ----
    embedding_provider: str = "huggingface"  # "huggingface" 本地模型 或 "openai" 云端 API
    huggingface_embedding_model: str = "BAAI/bge-small-zh-v1.5"
    openai_embedding_model: str = "text-embedding-3-small"

    # ---- Chroma 向量库 ----
    chroma_collection_name: str = "industry_intelligence"

    # ---- 文本切片参数 ----
    default_chunk_size: int = 800
    default_chunk_overlap: int = 120
    default_top_k: int = 4  # 检索时默认返回的文档数

    # ---- Demo 认证（当前未启用） ----
    demo_username: str | None = Field(default=None, repr=False)
    demo_password: str | None = Field(default=None, repr=False)


@lru_cache
def get_settings() -> Settings:
    """返回 Settings 的单例实例。被几乎所有模块调用。"""
    return Settings()
