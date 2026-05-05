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
