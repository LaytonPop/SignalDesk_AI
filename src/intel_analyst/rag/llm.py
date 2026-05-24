"""
LLM 模型工厂。

根据配置中 llm_provider 的值，返回对应的 Chat 模型实例：
    - "openai" → ChatOpenAI（走 DeepSeek/OpenAI 兼容 API，temperature=0.2 以保证答案稳定性）
    - "ollama" → ChatOllama（本地 Ollama 服务）

被 QueryService.__init__() 和 ReportService.__init__() 调用。
"""

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from intel_analyst.core.config import get_settings


def build_chat_model():
    settings = get_settings()
    if settings.llm_provider == "openai":
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            temperature=0.2,
        )
    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=0.2,
    )
