from sentence_transformers import SentenceTransformer
import faiss
import pandas as pd
from data_loader import load_data_from_sheet

# โหลดข้อมูลจาก Google Sheet
df = load_data_from_sheet()

# เตรียมข้อความที่ใช้สำหรับการฝัง (embedding)
def prepare_text(row):
    name = str(row.get("ชื่อสินค้า", "")).strip()
    code = str(row.get("รหัสสินค้า", "")).strip()
    tag = str(row.get("Tag", "")).strip()
    return f"{name} {code} {tag}"

# เตรียมข้อมูลฝัง vector
texts = df.apply(prepare_text, axis=1).tolist()

model = SentenceTransformer("all-MiniLM-L6-v2")
text_vectors = model.encode(texts)

index = faiss.IndexFlatL2(text_vectors[0].shape[0])
index.add(text_vectors)

def search_faiss(query, top_k=3):
    query_vector = model.encode([query.strip()])
    D, I = index.search(query_vector, top_k)

    results = []
    for i in I[0]:
        if i < len(df):
            row = df.iloc[i]
            item_text = f"{row['ชื่อสินค้า']} (รหัส {row['รหัสสินค้า']}) - ราคา {row['ราคาขาย']} บาท"
            results.append(item_text)

    return "\n".join(results)
