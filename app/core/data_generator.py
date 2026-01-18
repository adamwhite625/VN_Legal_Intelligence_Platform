import json
import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

# --- CẤU HÌNH ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INPUT_FILE = "app/core/raw_law_data.json"
OUTPUT_FILE = "app/core/ready_to_import_dataset.json"

# Đặt mục tiêu cao (10.000) để đảm bảo chạy hết toàn bộ các bộ luật
TARGET_ROWS = 10000 

# Sử dụng gpt-4o-mini
llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.8 # Tăng sự sáng tạo cho các tình huống
)

# Prompt yêu cầu sinh câu hỏi tình huống cụ thể (Tiếng Việt có dấu)
prompt = ChatPromptTemplate.from_messages([
    ("system", """
    Bạn là chuyên gia dữ liệu pháp lý và luật sư tư vấn. Nhiệm vụ của bạn là tạo dữ liệu huấn luyện cho Chatbot AI.
    
    Quy trình làm việc:
    1. Đọc văn bản luật được cung cấp.
    2. Đóng vai người dân đang gặp rắc rối pháp lý, đặt 2-3 câu hỏi dạng tình huống thực tế (Case Study) liên quan trực tiếp đến điều luật đó.
    3. Trả về kết quả dưới dạng danh sách JSON.

    Yêu cầu về Câu hỏi (key: 'anchor'):
    - TUYỆT ĐỐI KHÔNG hỏi lý thuyết khô khan (Ví dụ: "Điều 1 quy định gì?", "Khái niệm X là gì?").
    - PHẢI hỏi dạng câu chuyện/tình huống cụ thể.
    - Sử dụng ngôi thứ nhất (Tôi, gia đình tôi, công ty chúng tôi, chồng tôi, vợ tôi...).
    - Thêm các chi tiết giả định để tăng tính chân thực (Ví dụ: "Tôi sinh năm 1985...", "Công ty tôi thành lập năm 2020...", "Vợ chồng tôi ly thân đã 2 năm...").

    Yêu cầu về Cấu trúc JSON trả về (Bắt buộc đúng từ khóa):
    [
      {{
        "anchor": "Viết câu hỏi tình huống số 1 vào đây...",
        "positive": "Trích dẫn nguyên văn nội dung luật vào đây..."
      }},
      {{
        "anchor": "Viết câu hỏi tình huống số 2 vào đây...",
        "positive": "Trích dẫn nguyên văn nội dung luật vào đây..."
      }}
    ]
    """),
    ("human", "Văn bản luật: {law_content}")
])

chain = prompt | llm | JsonOutputParser()

def generate_data():
    if not os.path.exists(INPUT_FILE):
        print(f"[LỖI] Không tìm thấy file {INPUT_FILE}")
        return

    print(f"[THÔNG TIN] Đang đọc dữ liệu thô từ: {INPUT_FILE}")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        articles = json.load(f)

    # --- KHỞI TẠO DỮ LIỆU CŨ (CƠ CHẾ SMART RESUME) ---
    final_dataset = []
    processed_articles = set() # Tập hợp các điều luật đã xử lý
    
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                final_dataset = json.load(f)
            
            # Quét qua dữ liệu cũ để đánh dấu những điều luật đã làm rồi
            for item in final_dataset:
                # Tạo key duy nhất: Tên luật + ID Điều
                key = f"{item['law_name']}_{item['law_id']}"
                processed_articles.add(key)
                
            print(f"[THÔNG TIN] Tìm thấy {len(final_dataset)} dòng dữ liệu cũ.")
            print(f"[THÔNG TIN] Đã xử lý xong {len(processed_articles)} điều luật trước đó. Sẽ tự động bỏ qua chúng.")
        except:
            pass

    print(f"[THÔNG TIN] BẮT ĐẦU SINH DỮ LIỆU (Mục tiêu tổng: {TARGET_ROWS} dòng)...")
    
    count_new = 0 # Đếm số lượng mới sinh ra trong phiên này
    
    for index, article in enumerate(articles):
        # Kiểm tra nếu tổng dữ liệu đã vượt quá mục tiêu thì dừng
        if len(final_dataset) >= TARGET_ROWS:
            print(f"\n[XONG] Đã đạt giới hạn {TARGET_ROWS} dòng dữ liệu.")
            break
        
        # --- LOGIC BỎ QUA (SKIP) ---
        current_key = f"{article.get('law_name', '')}_{article['article_id']}"
        if current_key in processed_articles:
            # Nếu điều luật này đã có trong file json rồi thì bỏ qua không làm lại
            continue 
        # ---------------------------

        try:
            print(f"   [Tổng: {len(final_dataset)} | Mới thêm: {count_new}] Đang xử lý: {article.get('law_name', '')} - {article['article_id']}...")
            
            # Gọi OpenAI
            response = chain.invoke({"law_content": article['content']})
            
            # Xử lý nếu OpenAI trả về dict thay vì list
            if isinstance(response, dict):
                response = [response]
            
            items_added = 0
            for item in response:
                question_text = item.get('anchor')
                
                # Kiểm tra kỹ dữ liệu (đôi khi AI dùng từ khóa khác)
                if not question_text:
                    question_text = item.get('question') # Thử key dự phòng
                
                if not question_text:
                    continue

                final_dataset.append({
                    "id": f"syn_{index}_{int(time.time())}_{items_added}",
                    "question": question_text,
                    "law_content": article['content'],
                    "law_id": article['article_id'],
                    "law_name": article.get('law_name', 'Unknown')
                })
                items_added += 1
            
            # Đánh dấu là đã xử lý xong điều luật này
            processed_articles.add(current_key)
            count_new += items_added
            
            # Lưu file mới khi xử lý được mỗi 15 điều luật mới (để an toàn)
            if count_new % 15 == 0:
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(final_dataset, f, ensure_ascii=False, indent=4)
                print(f"      -> Đã lưu file tạm thời ({len(final_dataset)} dòng).")


        except Exception as e:
            print(f"   [LỖI] Dòng {index}: {e}")
            continue

    # Lưu lần cuối cùng
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_dataset, f, ensure_ascii=False, indent=4)
    
    print(f"\n[HOÀN THÀNH] Tổng cộng {len(final_dataset)} dòng dữ liệu đã sẵn sàng!")

if __name__ == "__main__":
    generate_data()