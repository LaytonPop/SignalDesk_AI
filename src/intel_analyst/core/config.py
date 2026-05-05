from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="INTEL_ANALYST_",
        extra="ignore",
    )

    app_env: str = "dev"
    api_v1_prefix: str = "/api/v1"

    root_dir: Path = ROOT_DIR
    config_dir: Path = ROOT_DIR / "config"
    data_dir: Path = ROOT_DIR / "data"
    raw_data_dir: Path = ROOT_DIR / "data" / "raw"
    processed_data_dir: Path = ROOT_DIR / "data" / "processed"
    table_data_dir: Path = ROOT_DIR / "data" / "tables"
    report_data_dir: Path = ROOT_DIR / "data" / "reports"
    vectorstore_dir: Path = ROOT_DIR / "data" / "vectorstore"

    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"

    embedding_provider: str = "huggingface"
    huggingface_embedding_model: str = "BAAI/bge-small-zh-v1.5"

    openai_base_url: str | None = None
    openai_api_key: str | None = None
    openai_model: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"

    chroma_collection_name: str = "industry_intelligence"
    default_chunk_size: int = 800
    default_chunk_overlap: int = 120
    default_top_k: int = 4

    demo_username: str | None = Field(default=None, repr=False)
    demo_password: str | None = Field(default=None, repr=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
