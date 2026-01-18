import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sklearn.manifold import TSNE
import matplotlib.font_manager as fm

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = os.getenv("QDRANT_PORT", "6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "law_data")

def visualize_vectors():
    print(f"[THÔNG TIN] Đang kết nối đến Qdrant ({COLLECTION_NAME})...")
    client = QdrantClient(host=QDRANT_HOST, port=int(QDRANT_PORT))

    # --- SỬA ĐỔI QUAN TRỌNG ---
    # Tăng giới hạn lên 5000 để đảm bảo lấy hết 5 bộ luật (Tổng khoảng 3000-4000 dòng)
    limit = 5000 
    print(f"[THÔNG TIN] Đang tải tối đa {limit} vector để phân tích...")
    
    # Scroll để lấy dữ liệu
    records, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=limit,
        with_vectors=True
    )

    if not records:
        print("[LỖI] Không tìm thấy dữ liệu nào trong Qdrant.")
        return

    # 2. Tách vector và nhãn
    vectors = []
    labels = []
    
    for record in records:
        vectors.append(record.vector)
        # Lấy tên luật
        law_name = record.payload.get("loai_van_ban", "Khác")
        # Rút gọn tên hiển thị
        law_name = law_name.replace("Luật", "L.").replace("Bộ luật", "BL").replace("Việt Nam", "VN").replace("(Văn bản hợp nhất 2017)", "")
        labels.append(law_name)

    # In báo cáo số lượng để kiểm tra đủ 5 bộ chưa
    unique_labels = list(set(labels))
    print(f"[KIỂM TRA] Tìm thấy {len(unique_labels)} bộ luật trong dữ liệu tải về:")
    for l in unique_labels:
        count = labels.count(l)
        print(f"   - {l}: {count} mẫu")

    vectors = np.array(vectors)
    
    # 3. Giảm chiều dữ liệu
    print("[THÔNG TIN] Đang tính toán giảm chiều dữ liệu (t-SNE)... Quá trình này có thể mất 1-2 phút.")
    
    # perplexity=30 phù hợp với dữ liệu vài nghìn điểm
    tsne = TSNE(n_components=2, random_state=42, perplexity=30, init='random', learning_rate='auto')
    vectors_2d = tsne.fit_transform(vectors)

    # 4. Vẽ biểu đồ
    print("[THÔNG TIN] Đang vẽ biểu đồ...")
    plt.figure(figsize=(16, 12)) # Tăng kích thước ảnh
    
    sns.scatterplot(
        x=vectors_2d[:, 0], 
        y=vectors_2d[:, 1], 
        hue=labels, 
        palette="tab10", # Bảng màu hỗ trợ tốt 10 loại khác nhau
        s=50, 
        alpha=0.7,
        edgecolor=None
    )

    plt.title(f"BẢN ĐỒ DỮ LIỆU {len(vectors)} ĐIỀU LUẬT (t-SNE)", fontsize=16, fontweight='bold', color='#333333')
    plt.legend(title="Danh sách Bộ Luật", bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
    plt.grid(True, linestyle='--', alpha=0.3)
    
    # Căn chỉnh để không bị mất chú thích
    plt.tight_layout()
    
    output_img = "law_data_visualization.png"
    plt.savefig(output_img, dpi=300)
    print(f"[HOÀN TẤT] Đã lưu biểu đồ vào file: {output_img}")
    
    try:
        plt.show()
    except:
        pass

if __name__ == "__main__":
    visualize_vectors()