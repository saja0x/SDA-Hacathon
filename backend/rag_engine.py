"""
🏛️ RAG Engine – Saudi Labor Law System
Importable module adapted from rag.py

Pipeline:
1. Load data and smart chunking (by article / page)
2. Embedding using Arabic embed model
3. Store vectors in ChromaDB (semantic search)
4. Generation using OpenAI (GPT-4o-mini) via API
"""

import re
import os
import math
import warnings
from pathlib import Path
from typing import List, Dict, Tuple

import numpy as np
import nltk

from sentence_transformers import SentenceTransformer, util
import chromadb

from dotenv import load_dotenv
from openai import OpenAI

warnings.filterwarnings("ignore")
load_dotenv()

# ───────────────────────────── Config ─────────────────────────────
_BASE_DIR = Path(__file__).parent

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
EMBED_MODEL = os.getenv("EMBED_MODEL", "Omartificial-Intelligence-Space/Harrier-Arabic-Matryoshka-270m")
CHROMA_DIR = os.getenv("CHROMA_DIR", str(_BASE_DIR / "chroma_db"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "400"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "80"))
TOP_K = int(os.getenv("TOP_K", "5"))
DEVICE = os.getenv("DEVICE", "cpu")
DATASET_PATH = os.getenv("DATASET_PATH", str(_BASE_DIR / "data" / "ocr_result_rag_ready4.md"))

# ───────────────────────────── Module State ─────────────────────────────
_openai_client = None
_embed_model = None
_collection = None
_chunks = None
_initialized = False


def _get_openai_client():
    """Lazy-init OpenAI client."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


# ════════════════════════════════════════════════════════════════════════
# Tokenizer
# ════════════════════════════════════════════════════════════════════════
def arabic_tokenize(text: str) -> List[str]:
    """Simple whitespace + punctuation tokenizer for Arabic."""
    text = re.sub(r'[\u0640]', '', text)
    text = re.sub(r'[^\u0600-\u06FF\s]', ' ', text)  # keep Arabic only
    return [t for t in text.split() if len(t) > 1]


# ════════════════════════════════════════════════════════════════════════
# 1) Load data and chunking
# ════════════════════════════════════════════════════════════════════════
def load_and_chunk(path: str, chunk_size: int = CHUNK_SIZE,
                    overlap: int = CHUNK_OVERLAP) -> List[Dict]:
    """
    Strategy:
      1. Split on page boundaries (## page N)
      2. Within each page, split on article boundaries (Article ...)
      3. If a segment is still > chunk_size chars → sliding-window split
    Returns a list of dicts: {id, text, page, article_num, source}
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    # ── 1. Split by page ──────────────────────
    page_blocks = re.split(r"## الصفحة (\d+)", raw)
    pages = {}
    for i in range(1, len(page_blocks), 2):
        pnum = int(page_blocks[i])
        pages[pnum] = page_blocks[i + 1].strip()

    # ── 2. Extract article segments ───────────
    article_pattern = re.compile(
        r"(المادة\s+(?:الأولى|الثانية|الثالثة|الرابعة|الخامسة|السادسة|"
        r"السابعة|الثامنة|التاسعة|العاشرة|[\u0660-\u0669\d]+)"
        r"(?:\s*مكرر)?[^\n]*\n)",
        re.UNICODE,
    )

    chunks: List[Dict] = []
    chunk_id = 0

    for pnum, text in sorted(pages.items()):
        segments = article_pattern.split(text)
        i = 0
        while i < len(segments):
            seg = segments[i].strip()
            if not seg:
                i += 1
                continue

            # Detect article header
            art_match = article_pattern.match(seg)
            article_label = ""
            if art_match:
                # Merge header with body
                header = seg
                body = segments[i + 1].strip() if i + 1 < len(segments) else ""
                seg = (header + "\n" + body).strip()
                article_label = header.strip()
                i += 2
            else:
                i += 1

            # ── 3. Sliding window if too long ──
            if len(seg) <= chunk_size:
                if len(seg) > 30:
                    chunks.append({
                        "id": f"chunk_{chunk_id:04d}",
                        "text": seg,
                        "page": pnum,
                        "article": article_label,
                        "source": f"page_{pnum}",
                    })
                    chunk_id += 1
            else:
                words = seg.split()
                buf, char_count = [], 0
                for w in words:
                    buf.append(w)
                    char_count += len(w) + 1
                    if char_count >= chunk_size:
                        chunk_text = " ".join(buf).strip()
                        if len(chunk_text) > 30:
                            chunks.append({
                                "id": f"chunk_{chunk_id:04d}",
                                "text": chunk_text,
                                "page": pnum,
                                "article": article_label,
                                "source": f"page_{pnum}",
                            })
                            chunk_id += 1
                        overlap_words = buf[-max(1, len(buf) // 5):]
                        buf = overlap_words
                        char_count = sum(len(w) + 1 for w in buf)
                if buf:
                    chunk_text = " ".join(buf).strip()
                    if len(chunk_text) > 30:
                        chunks.append({
                            "id": f"chunk_{chunk_id:04d}",
                            "text": chunk_text,
                            "page": pnum,
                            "article": article_label,
                            "source": f"page_{pnum}",
                        })
                        chunk_id += 1

    return chunks


# ════════════════════════════════════════════════════════════════════════
# 2) Load embedding model
# ════════════════════════════════════════════════════════════════════════
def load_embedding_model(model_name: str = EMBED_MODEL, device: str = DEVICE) -> SentenceTransformer:
    print(f"[RAG] Loading embedding model: {model_name} ...")
    model = SentenceTransformer(model_name, device=device)
    print(f"[RAG] Model loaded | Embedding dim: {model.get_sentence_embedding_dimension()}")

    _test = model.encode([
        "Saudi labor contract",
        "Employment system and wages",
    ])
    _sim = util.cos_sim(_test[0], _test[1]).item()
    print(f"[RAG] Similarity smoke-test (should be > 0.5): {_sim:.4f}")
    return model


# ════════════════════════════════════════════════════════════════════════
# 3) Build ChromaDB
# ════════════════════════════════════════════════════════════════════════
def build_chroma_collection(chunks, embed_model,
                            chroma_dir=CHROMA_DIR,
                            batch_size=64):

    os.makedirs(chroma_dir, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=chroma_dir)

    # ✅ CHECK IF COLLECTION EXISTS
    try:
        collection = chroma_client.get_collection(name="sa_employment")
        print("[RAG] ✅ Loaded existing ChromaDB collection")
        return collection
    except Exception:
        print("[RAG] ⚙️ Building new ChromaDB collection...")

    # ── build only if not exists ──
    collection = chroma_client.create_collection(
        name="sa_employment",
        metadata={"hnsw:space": "cosine"},
    )

    texts = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metadatas = [{"page": c["page"], "article": c["article"],
                  "source": c["source"]} for c in chunks]

    embeddings = embed_model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    for i in range(0, len(texts), batch_size):
        sl = slice(i, i + batch_size)
        collection.add(
            ids=ids[sl],
            documents=texts[sl],
            embeddings=embeddings[sl].tolist(),
            metadatas=metadatas[sl],
        )

    print(f"[RAG] ✅ Built ChromaDB with {collection.count()} docs")
    return collection


# ════════════════════════════════════════════════════════════════════════
# 4) Semantic Search
# ════════════════════════════════════════════════════════════════════════
def semantic_search(query: str, collection, embed_model: SentenceTransformer,
                     top_k: int = TOP_K) -> List[Dict]:
    """Cosine similarity search via ChromaDB."""
    q_emb = embed_model.encode([query], normalize_embeddings=True).tolist()

    results = collection.query(
        query_embeddings=q_emb,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for i in range(len(results["ids"][0])):
        distance = results["distances"][0][i]
        hits.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "meta": results["metadatas"][0][i],
            "distance": distance,
            "score": 1 - distance,
            "method": "semantic",
        })

    return hits


# ════════════════════════════════════════════════════════════════════════
# 5) Generation (OpenAI GPT-4o-mini)
# ════════════════════════════════════════════════════════════════════════
def build_prompt(query: str, contexts: List[Dict]) -> Tuple[str, str]:
    """Build system and user prompts for OpenAI."""
    ctx_text = "\n\n".join([f"- {c['text']}" for c in contexts[:3]])

    system_prompt = (
        "Answer only using the provided legal texts. "
        "If not found, respond with 'Not mentioned in the regulation'. "
        "Do not hallucinate."
    )

    user_prompt = (
        f"Legal texts:\n{ctx_text}\n"
        f"Question: {query}\n"
        "Answer strictly based on the text:"
    )

    return system_prompt, user_prompt


def generate_answer(query: str, contexts: List[Dict],
                     model: str = OPENAI_MODEL,
                     max_new_tokens: int = 250,
                     temperature: float = 0.3) -> str:
    """Generate answer using OpenAI."""
    system_prompt, user_prompt = build_prompt(query, contexts)
    client = _get_openai_client()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_new_tokens,
        temperature=temperature,
    )

    return response.choices[0].message.content.strip()


# ════════════════════════════════════════════════════════════════════════
# 6) Retrieval Evaluation
# ════════════════════════════════════════════════════════════════════════
def build_test_pairs(chunks: List[Dict], n: int = 100) -> List[Dict]:
    """Create synthetic evaluation pairs for retrieval testing."""
    pairs = []
    candidate_chunks = [c for c in chunks if len(c["text"]) > 50]
    if not candidate_chunks:
        return []
    step = max(1, len(candidate_chunks) // min(n, len(candidate_chunks)))
    for c in candidate_chunks[::step][:n]:
        sentences = [s.strip() for s in re.split(r'[.،؛\n]', c["text"]) if len(s.strip()) > 20]
        if not sentences:
            continue
        key = sentences[0][:80]
        art = c["article"].strip()
        question = f"What is the rule about {art}?" if art else f"What is mentioned about: {key}?"
        pairs.append({"question": question, "relevant_id": c["id"], "relevant_text": c["text"]})
    return pairs


def reciprocal_rank(relevant_id: str, results: List[Dict]) -> float:
    for rank, r in enumerate(results, 1):
        if r["id"] == relevant_id:
            return 1.0 / rank
    return 0.0


def recall_at_k(relevant_id: str, results: List[Dict], k: int) -> float:
    return float(any(r["id"] == relevant_id for r in results[:k]))


def dcg_at_k(relevant_id: str, results: List[Dict], k: int) -> float:
    for rank, r in enumerate(results[:k], 1):
        if r["id"] == relevant_id:
            return 1.0 / math.log2(rank + 1)
    return 0.0


def ndcg_at_k(relevant_id: str, results: List[Dict], k: int) -> float:
    return dcg_at_k(relevant_id, results, k)


# ════════════════════════════════════════════════════════════════════════
# 7) Generation Evaluation
# ════════════════════════════════════════════════════════════════════════
def hallucination_score(answer: str, contexts: List[Dict]) -> float:
    """Token-level hallucination ratio."""
    ctx_tokens = set()
    for c in contexts:
        ctx_tokens.update(arabic_tokenize(c["text"]))
    ans_tokens = arabic_tokenize(answer)
    if not ans_tokens:
        return 0.0
    missing = sum(1 for t in ans_tokens if t not in ctx_tokens)
    return missing / len(ans_tokens)


def faithfulness_score(answer: str, contexts: List[Dict]) -> float:
    return 1.0 - hallucination_score(answer, contexts)


# ════════════════════════════════════════════════════════════════════════
# 8) Full RAG Pipeline
# ════════════════════════════════════════════════════════════════════════
def rag_answer(question: str, collection, embed_model: SentenceTransformer,
               top_k: int = TOP_K, max_new_tokens: int = 250,
               verbose: bool = True) -> Dict:
    """End-to-end RAG pipeline."""
    ctx = semantic_search(question, collection, embed_model, top_k)

    answer = generate_answer(question, ctx, max_new_tokens=max_new_tokens)

    faith = faithfulness_score(answer, ctx)
    hall = hallucination_score(answer, ctx)

    result = {
        "question": question,
        "answer": answer,
        "faithfulness": round(faith, 4),
        "hallucination": round(hall, 4),
        "num_contexts": len(ctx),
        "contexts": ctx,
    }

    if verbose:
        print("=" * 60)
        print(f"Question: {question}")
        print(f"Contexts retrieved: {len(ctx)}")
        print(f"Answer: {answer}")
        print(f"Faithfulness: {faith:.2%} | Hallucination: {hall:.2%}")

    return result


# ════════════════════════════════════════════════════════════════════════
# 9) Visualization
# ════════════════════════════════════════════════════════════════════════
def plot_dashboard(eval_results: Dict, gen_metrics: Dict, k_values: List[int] = (1, 3, 5, 10),
                    output_path: str = "rag_evaluation.png"):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle("RAG Evaluation Dashboard")

        ax = axes[0]
        for metric in ["Recall", "NDCG", "MRR"]:
            y = [np.mean(eval_results[f"{metric}@{k}"]) for k in k_values]
            ax.plot(k_values, y, marker="o", label=metric)
        ax.set_title("Retrieval Metrics")

        ax = axes[1]
        gen_vals = [
            np.mean(gen_metrics["rouge1"]),
            np.mean(gen_metrics["rougeL"]),
            np.mean(gen_metrics["bert_f1"]),
            np.mean(gen_metrics["faithfulness"]),
        ]
        ax.bar(["ROUGE1", "ROUGE-L", "BERT", "Faithfulness"], gen_vals)

        plt.tight_layout()
        plt.savefig(output_path)
        print(f"Plot saved: {output_path}")

    except Exception as e:
        print(f"Plot skipped: {e}")


# ════════════════════════════════════════════════════════════════════════
# Initialization & Convenience API
# ════════════════════════════════════════════════════════════════════════
def init_rag(dataset_path: str = None):
    """
    Initialize the RAG system. Call once at application startup.
    Loads the dataset, builds embeddings, and prepares ChromaDB.
    """
    global _embed_model, _collection, _chunks, _initialized

    if _initialized:
        print("[RAG] Already initialized, skipping.")
        return

    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)

    path = dataset_path or DATASET_PATH
    print(f"[RAG] Device: {DEVICE}")
    print(f"[RAG] OpenAI model for generation: {OPENAI_MODEL}")
    print(f"[RAG] Loading dataset from: {path}")

    _chunks = load_and_chunk(path)
    print(f"[RAG] Loaded {len(_chunks)} chunks")

    _embed_model = load_embedding_model()
    _collection = build_chroma_collection(_chunks, _embed_model)

    _initialized = True
    print("[RAG] ✅ RAG system initialized and ready")


def search(query: str, top_k: int = TOP_K) -> List[Dict]:
    """Convenience: semantic search (requires init_rag() first)."""
    if not _initialized:
        raise RuntimeError("RAG not initialized. Call init_rag() first.")
    return semantic_search(query, _collection, _embed_model, top_k)


def get_answer(question: str, top_k: int = TOP_K, verbose: bool = False) -> Dict:
    """Convenience: full RAG pipeline (requires init_rag() first)."""
    if not _initialized:
        raise RuntimeError("RAG not initialized. Call init_rag() first.")
    return rag_answer(question, _collection, _embed_model, top_k, verbose=verbose)


def is_initialized() -> bool:
    """Check if the RAG system has been initialized."""
    return _initialized
