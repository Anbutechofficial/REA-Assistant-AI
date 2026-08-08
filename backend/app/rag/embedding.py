import os
import json
import pandas as pd
from sentence_transformers import SentenceTransformer


def generate_embeddings():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.abspath(os.path.join(base_dir, "..", "uploads"))
    csv_path = os.path.join(uploads_dir, "Real_Estate_Assistant.csv")
    json_path = os.path.join(uploads_dir, "embeddings.json")

    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    print(f"Reading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)

    print(f"Loaded {len(df)} rows. Loading SentenceTransformer model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    texts = [
        f"{row.get('name', '')} in {row.get('location', '')}: {row.get('bhk', '')} BHK, {row.get('area_sqft', '')} sqft, Rs {row.get('price_lakhs', '')} Lakhs"
        for _, row in df.iterrows()
    ]

    print("Generating embeddings for all properties...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    documents = []
    for (_, row), text, emb in zip(df.iterrows(), texts, embeddings):
        doc = row.to_dict()
        doc["text"] = text
        doc["embedding"] = emb
        documents.append(doc)

    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2)

    print(f"Successfully generated and saved {len(documents)} property embeddings to {json_path}!")


if __name__ == "__main__":
    generate_embeddings()
