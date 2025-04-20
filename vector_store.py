import os
import pickle
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
from data_loader import load_data_from_sheet

# === CONFIG ===
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
PICKLE_PATH = "faiss_index.pkl"

# === โหลด Vector Index (แบบ lazy + cache) ===
def load_or_build_faiss():
    if os.path.exists(PICKLE_PATH):
        with open(PICKLE_PATH, "rb") as f:
            index, df = pickle.load(f)
        return index, df

    print("🔄 Building FAISS Index...")
    df = load_data_from_sheet()
    model = SentenceTransformer(MODEL_NAME)

    corpus = df["ชื่อสินค้า"].astype(str).tolist()
    vectors = model.encode(corpus, show_progress_bar=False)

    index = faiss.IndexFlatL2(vectors[0].shape[0])
    index.add(vectors)

    with open(PICKLE_PATH, "wb") as f:
        pickle.dump((index, df), f)

    return index, df

# === ใช้ค้นหาสินค้าแบบ vector similarity ===
def search_faiss(query, top_k=3):
    index, df = load_or_build_faiss()
    model = SentenceTransformer(MODEL_NAME)
    query_vector = model.encode([query])

    D, I = index.search(query_vector, top_k)

    results = []
    for i in I[0]:
        if i < len(df):
            row = df.iloc[i]
            name = str(row.get("ชื่อสินค้า", "-"))
            code = str(row.get("รหัสสินค้า", "-"))
            price = str(row.get("ราคาขาย", "-"))
            item_text = f"{name} (รหัส {code}) - ราคา {price} บาท"
            results.append(item_text)

    return "\n".join(results)
