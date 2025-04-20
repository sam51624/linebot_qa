from sentence_transformers import SentenceTransformer
import faiss
import pandas as pd
from data_loader import load_data_from_sheet

# โหลดข้อมูล + สร้าง vector index (โหลดครั้งเดียว)
df = load_data_from_sheet()
model = SentenceTransformer("all-MiniLM-L6-v2")
corpus = df["ชื่อสินค้า"].astype(str).tolist()
corpus_vectors = model.encode(corpus)

index = faiss.IndexFlatL2(corpus_vectors[0].shape[0])
index.add(corpus_vectors)

def search_faiss(query, top_k=3):
    query_vector = model.encode([query])
    D, I = index.search(query_vector, top_k)

    results = []
    for i in I[0]:
        if i < len(df):
            row = df.iloc[i]
            item_text = f"{row['ชื่อสินค้า']} (รหัส {row['รหัสสินค้า']}) - ราคา {row['ราคาขาย']} บาท"
            results.append(item_text)

    return "\n".join(results)

