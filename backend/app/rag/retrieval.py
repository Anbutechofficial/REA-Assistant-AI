import os
import time
import json
import numpy as np
import certifi
import pandas as pd
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient

from app.core.config import Setting
from app.rag.vector_store import VectorStore

# Load environment variables
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, "..", "..", ".env"))

_vector_store = VectorStore()
_st_model = None


def get_sentence_model():
    global _st_model
    if _st_model is None:
        _st_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _st_model


def get_query_embedding(query: str) -> list[float]:
    """Generate embedding for query using Gemini API or SentenceTransformers."""
    gemini_key = Setting.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

    if gemini_key:
        for attempt in range(2):
            try:
                from google import genai
                from google.genai import types
                gemini_client = genai.Client(api_key=gemini_key)
                res = gemini_client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=query,
                    config=types.EmbedContentConfig(output_dimensionality=768),
                )
                if hasattr(res, "embeddings") and res.embeddings:
                    return list(res.embeddings[0].values)
                if hasattr(res, "embedding") and hasattr(res.embedding, "values"):
                    return list(res.embedding.values)
            except Exception as e:
                if ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)) and attempt < 1:
                    time.sleep(2)
                else:
                    print(f"Gemini query embedding unavailable ({e}). Falling back to SentenceTransformer.")
                    break

    try:
        st_model = get_sentence_model()
        emb = st_model.encode(query).tolist()
        if len(emb) < 768:
            emb = emb + [0.0] * (768 - len(emb))
        return emb[:768]
    except Exception as e:
        print(f"SentenceTransformer embedding failed: {e}")
        return []


def load_local_properties():
    embeddings_file = os.path.abspath(os.path.join(base_dir, "..", "uploads", "embeddings.json"))
    if not os.path.exists(embeddings_file):
        embeddings_file = os.path.abspath(os.path.join(base_dir, "..", "..", "data", "embeddings.json"))

    if os.path.exists(embeddings_file):
        try:
            with open(embeddings_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            pass
    return []


def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1, dtype=float)
    vec2 = np.array(vec2, dtype=float)
    if vec1.shape != vec2.shape:
        return 0.0
    norm1, norm2 = np.linalg.norm(vec1), np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (norm1 * norm2))


async def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """
    Retrieve top_k matching documents using MongoDB Atlas VectorStore (Hybrid Search: Vector + Keyword RRF).
    Falls back to local embedding cosine similarity if Atlas search is empty or uninitialized.
    """
    query_embedding = get_query_embedding(query)

    # 1. Primary: VectorStore Hybrid Search in MongoDB Atlas
    if query_embedding:
        try:
            matches = await _vector_store.hybrid_search(
                query_text=query,
                query_embedding=query_embedding,
                top_k=top_k
            )
            if matches:
                return [
                    {
                        "score": m.get("score", 0.0),
                        "text": m.get("text", "")
                    }
                    for m in matches
                ]
        except Exception as e:
            print(f"VectorStore hybrid search encountered an issue: {e}")

    # 2. Fallback: Local JSON Embeddings
    local_docs = load_local_properties()
    if local_docs and query_embedding:
        scores = []
        for doc in local_docs:
            doc_emb = doc.get("embedding")
            text_content = doc.get("text", "")
            if doc_emb and len(doc_emb) == len(query_embedding):
                score = cosine_similarity(query_embedding, doc_emb)
            else:
                score = 0.0
            scores.append({"score": score, "text": text_content})
        scores.sort(key=lambda x: x["score"], reverse=True)
        if scores and scores[0]["score"] > 0:
            return scores[:top_k]

    # 3. Ultimate Fallback: Direct CSV keyword matching
    csv_file = os.path.abspath(os.path.join(base_dir, "..", "uploads", "Real_Estate_Assistant.csv"))
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
            keywords = [w.lower() for w in query.replace("?", "").replace(",", "").split() if len(w) > 1]
            matches = []
            for _, row in df.iterrows():
                row_str = f"{row.get('name', '')} in {row.get('location', '')}: {row.get('bhk', '')} BHK, {row.get('area_sqft', '')} sqft, Rs {row.get('price_lakhs', '')} Lakhs"
                row_lower = row_str.lower()
                
                # Check for BHK matching (e.g. 3bhk or 3 bhk)
                clean_q = query.lower().replace(" ", "")
                if "3bhk" in clean_q or ("3" in keywords and "bhk" in clean_q):
                    if str(row.get("bhk", "")).strip().startswith("3") or "3 bhk" in row_lower:
                        matches.append({"score": 0.9, "text": row_str})
                elif any(k in row_lower for k in keywords):
                    matches.append({"score": 0.5, "text": row_str})
            if matches:
                return matches[:top_k]
        except Exception as ex:
            print(f"CSV fallback search exception: {ex}")

    return []

