"""End-to-end test of embeddings + Chroma + LLM."""
import sys, os, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

t0 = time.time()

# 1. Embeddings
print("[1/3] Loading embeddings...", flush=True)
from intel_analyst.rag.embeddings import build_embeddings
emb = build_embeddings()
test_vec = emb.embed_query("test")
print(f"  OK ({time.time()-t0:.1f}s) — dim={len(test_vec)}", flush=True)

# 2. Vector store
print("[2/3] Initializing Chroma...", flush=True)
from intel_analyst.rag.vector_store import VectorStoreManager
vs = VectorStoreManager()
docs = vs.similarity_search("半导体行业趋势", top_k=2)
print(f"  OK ({time.time()-t0:.1f}s) — found {len(docs)} docs", flush=True)

# 3. LLM
print("[3/3] Testing DeepSeek via LangChain...", flush=True)
from intel_analyst.rag.llm import build_chat_model
llm = build_chat_model()
resp = llm.invoke("你好，请用一句话介绍你自己。")
print(f"  OK ({time.time()-t0:.1f}s) — response: {resp.content[:100]}", flush=True)

print(f"\nALL PASSED in {time.time()-t0:.1f}s", flush=True)
