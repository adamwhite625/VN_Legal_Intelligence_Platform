import json
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# Cấu hình Qdrant
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = os.getenv("QDRANT_PORT", "6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "law_data")
DATA_FILE = "app/core/ready_to_import_dataset.json"

client = QdrantClient(host=QDRANT_HOST, port=int(QDRANT_PORT))

# --- SỬA ĐỔI TẠI ĐÂY ---
# Chuyển sang model Multilingual (Hỗ trợ 50+ ngôn ngữ bao gồm Tiếng Việt)
# Model này rất nhẹ, nhanh và không bị lỗi quyền truy cập (401)
print("[THÔNG TIN] Đang tải model Embedding (lần đầu sẽ hơi lâu)...")
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={"device": "cpu"}
)
# -----------------------

def import_to_qdrant():
    if not os.path.exists(DATA_FILE):
        print(f"[LỖI] Không tìm thấy file {DATA_FILE}. Hãy chạy data_generator.py trước!")
        return

    print(f"[THÔNG TIN] Đang đọc dữ liệu từ {DATA_FILE}...")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # Tạo Collection (Nếu chưa có)
    try:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE), # Lưu ý: Model mới này có vector size là 384
        )
        print(f"[OK] Đã tạo collection: {COLLECTION_NAME}")
    except Exception:
        print(f"[THÔNG TIN] Collection {COLLECTION_NAME} đã tồn tại, sẽ ghi thêm dữ liệu.")

    points = []
    print(f"[THÔNG TIN] Bắt đầu nạp {len(dataset)} dòng dữ liệu vào Qdrant...")
    
    for idx, item in enumerate(dataset):
        try:
            # Vector hóa nội dung
            text_to_embed = f"{item['law_name']} {item['question']} {item['law_content']}"
            vector = embeddings_model.embed_query(text_to_embed)
            
            payload = {
                "question_sample": item['question'],
                "combine_Article_Content": item['law_content'],
                "so_hieu": item['law_id'],
                "loai_van_ban": item['law_name'],
                "page_content": item['law_content']
            }
            
            points.append(PointStruct(id=idx, vector=vector, payload=payload))

            # Batch Upload
            if len(points) >= 50:
                client.upsert(collection_name=COLLECTION_NAME, points=points)
                print(f"   -> Đã nạp lô {idx+1}/{len(dataset)}...")
                points = [] 

        except Exception as e:
            print(f"   [CẢNH BÁO] Lỗi dòng {idx}: {e}")

    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
    
    print("\n[HOAN TẤT] Dữ liệu đã sẵn sàng trong Qdrant.")

if __name__ == "__main__":
    import_to_qdrant()