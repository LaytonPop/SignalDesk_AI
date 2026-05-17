"""Quick test script — test vector store and LLM independently."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from intel_analyst.rag.vector_store import VectorStoreManager
from intel_analyst.rag.llm import build_chat_model

# 1. Test vector store
print("=== Vector store ===")
vs = VectorStoreManager()
docs = vs.similarity_search("半导体行业趋势", top_k=2)
print(f"Found {len(docs)} docs")

# 2. Test LLM directly
print("\n=== LLM ===")
llm = build_chat_model()
resp = llm.invoke("你好，请用一句话介绍你自己。")
print(f"Response: {resp.content[:200]}")
print("\nSUCCESS: LLM works!")
