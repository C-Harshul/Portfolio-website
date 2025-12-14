import os
from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
import requests
import time
from typing import List
import numpy as np
from tqdm import tqdm

load_dotenv()

# Environment configuration for Cloudflare embeddings
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "<YOUR_ACCOUNT_ID>")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "<YOUR_API_TOKEN>")

# Embedding model per Cloudflare docs
CF_EMBEDDINGS_MODEL = "@cf/baai/bge-base-en-v1.5"  # 768-dim

if any(v.startswith("<YOUR_") for v in [CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN]):
    print("WARNING: Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN in your environment or edit this cell.")

# Cloudflare Workers AI Embeddings (REST client)

class CFWorkersAIEmbeddings:
    """
    Minimal client for Workers AI embeddings endpoint.
    POST https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}
    Body: {"text": "<string>"}
    Returns: {"result": {"data": [[...]]}} or {"data": [...]}
    """

    def __init__(self, account_id: str, api_token: str, model: str):
        self.base = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    def embed_one(self, text: str, retries: int = 3, backoff: float = 1.5) -> np.ndarray:
        payload = {"text": text}
        last_err = None
        for attempt in range(1, retries + 1):
            try:
                r = requests.post(self.base, headers=self.headers, json=payload, timeout=60)
                if r.status_code == 200:
                    data = r.json()
                    vec = None
                    if isinstance(data, dict) and "result" in data:
                        result = data["result"]
                        if "data" in result and result["data"]:
                            first = result["data"][0]
                            vec = first if isinstance(first, list) else result["data"]
                    elif "data" in data:
                        first = data["data"][0] if isinstance(data["data"], list) and data["data"] and isinstance(data["data"][0], list) else data["data"]
                        vec = first
                    if vec is None:
                        raise ValueError(f"Unexpected response structure: {data}")
                    return np.array(vec, dtype=np.float32)
                else:
                    last_err = RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
            except Exception as e:
                last_err = e
            time.sleep(backoff ** (attempt - 1))
        raise last_err

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        vectors = []
        for t in tqdm(texts, desc="Embedding with Cloudflare Workers AI"):
            vectors.append(self.embed_one(t))
        return np.vstack(vectors)

cf_embedder = CFWorkersAIEmbeddings(
    account_id=CLOUDFLARE_ACCOUNT_ID,
    api_token=CLOUDFLARE_API_TOKEN,
    model=CF_EMBEDDINGS_MODEL,
)


class GSTEmbeddings(Embeddings):
    """LangChain-compatible embeddings wrapper for GST documents."""
    
    def __init__(self, embedding_client):
        """Initialize with embedding client."""
        self.embedding_client = embedding_client
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        embeddings = self.embedding_client.embed_batch(texts)
        return embeddings.tolist()
        
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        embedding = self.embedding_client.embed_one(text)
        return embedding.tolist()

