import re
import json
import time
from playwright.sync_api import sync_playwright

# Danh sách các bộ luật cần cào (Đã sửa lại link tps -> https)
TARGETS = [
    {
        "name": "Luật Doanh nghiệp 2020",
        "url": "https://thuvienphapluat.vn/van-ban/Doanh-nghiep/Luat-Doanh-nghiep-so-59-2020-QH14-427301.aspx"
    },
    {
        "name": "Bộ luật Dân sự 2015",
        "url": "https://thuvienphapluat.vn/van-ban/Quyen-dan-su/Bo-luat-dan-su-2015-296215.aspx"
    },
    {
        "name": "Luật Hôn nhân và Gia đình 2014",
        "url": "https://thuvienphapluat.vn/van-ban/Quyen-dan-su/Luat-Hon-nhan-va-gia-dinh-2014-238640.aspx"
    },
    {
        "name": "Bộ luật Lao động 2019",
        "url": "https://thuvienphapluat.vn/van-ban/Lao-dong-Tien-luong/Bo-Luat-lao-dong-2019-333670.aspx"
    },
    {
        "name": "Bộ luật Hình sự (Văn bản hợp nhất 2017)",
        "url": "https://thuvienphapluat.vn/van-ban/Bo-may-hanh-chinh/Van-ban-hop-nhat-01-VBHN-VPQH-2017-Bo-luat-Hinh-su-363655.aspx"
    }
]

def clean_text(text):
    """Làm sạch văn bản: xóa khoảng trắng thừa"""
    # Thay thế các khoảng trắng đặc biệt và xuống dòng thừa bằng 1 dấu cách
    text = re.sub(r'\s+', ' ', text) 
    return text.strip()

def parse_articles(full_text):
    """Cắt văn bản lớn thành từng điều luật"""
    articles = []
    
    # Regex tìm: "Điều <số>." hoặc "Điều <số>:" ở đầu dòng/câu
    # (?=...) là điều kiện dừng khi gặp "Điều" tiếp theo hoặc hết văn bản
    pattern = r"(Điều\s+\d+[\.:].*?)(?=Điều\s+\d+[\.:]|$)"
    
    matches = re.findall(pattern, full_text, re.DOTALL)
    
    for match in matches:
        match = clean_text(match)
        
        # Lọc rác: Điều luật phải dài hơn 50 ký tự
        if len(match) < 50: continue

        # Trích xuất số hiệu (Ví dụ: Điều 1)
        id_match = re.search(r"Điều\s+(\d+)", match)
        article_id = f"Điều {id_match.group(1)}" if id_match else "Điều ?"
        
        # Tạo tiêu đề ngắn để dễ nhìn (20 từ đầu tiên)
        title_words = match.split()[:20]
        title = " ".join(title_words) + "..."

        articles.append({
            "article_id": article_id,
            "article_title": title,
            "content": match
        })
    
    return articles

def run_scraper():
    all_data = []
    
    print("BẮT ĐẦU CÀO DỮ LIỆU TỪ THƯ VIỆN PHÁP LUẬT (MULTI-URL)...")
    
    with sync_playwright() as p:
        # headless=False để bạn quan sát được quá trình chạy
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for target in TARGETS:
            print(f"\nĐang truy cập: {target['name']}...")
            try:
                # 1. Truy cập trang web
                page.goto(target['url'], timeout=90000) # Timeout 90s vì luật hình sự rất dài
                
                # 2. Chờ khung nội dung xuất hiện (divContentDoc hoặc content1)
                try:
                    page.wait_for_selector("#divContentDoc, .content1", timeout=15000)
                    print("Đã tải xong giao diện.")
                except:
                    print("Load lâu hoặc không thấy khung chuẩn, thử lấy dữ liệu ngay...")

                # 3. Cuộn trang xuống cuối để kích hoạt tải hết nội dung (nếu có lazy load)
                # Thư viện pháp luật đôi khi load nội dung dài dần dần
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2) 

                # 4. Lấy toàn bộ text trong khung nội dung
                full_text = page.evaluate("""() => {
                    // Ưu tiên các ID/Class chứa nội dung chính
                    const content = document.querySelector('#divContentDoc') || document.querySelector('.content1') || document.body;
                    
                    // Xóa quảng cáo, script, style, nút in ấn
                    const junk = content.querySelectorAll('.ads, script, style, .no-print, iframe, .relate-link');
                    junk.forEach(el => el.remove());

                    return content.innerText;
                }""")
                
                print(f"Đã tải văn bản thô: {len(full_text)} ký tự.")
                
                # 5. Cắt điều luật
                if len(full_text) > 2000: # Luật ngắn nhất cũng vài nghìn ký tự
                    articles = parse_articles(full_text)
                    print(f"Tách được: {len(articles)} điều luật.")
                    
                    # Gắn thêm tên luật vào mỗi điều để dễ phân biệt sau này
                    for art in articles:
                        art['law_name'] = target['name']
                        
                    all_data.extend(articles)
                else:
                    print("Nội dung quá ngắn. Có thể bị chặn hoặc bắt đăng nhập.")
                
                # Nghỉ 3 giây trước khi qua trang mới để tránh bị ban IP
                time.sleep(3)
                
            except Exception as e:
                print(f"Lỗi khi xử lý {target['name']}: {e}")
        
        browser.close()

    # --- TỔNG KẾT & LƯU FILE ---
    print(f"\n==========================================")
    
    # Lọc trùng lặp: Key = Tên luật + ID điều + 20 ký tự đầu
    unique_data = {}
    for item in all_data:
        # Ví dụ key: "Luật Doanh nghiệp 2020_Điều 1_Luật này quy định..."
        key = f"{item.get('law_name', '')}_{item['article_id']}_{item['content'][:20]}"
        unique_data[key] = item
    
    final_result = list(unique_data.values())
    
    print(f"TỔNG KẾT: Thu thập được TỔNG CỘNG {len(final_result)} điều luật.")
    print(f"==========================================")

    if final_result:
        with open("raw_law_data.json", "w", encoding="utf-8") as f:
            json.dump(final_result, f, ensure_ascii=False, indent=4)
        print("Đã lưu tất cả vào file: raw_law_data.json")
        print("SẴN SÀNG! Hãy chạy 'python app/core/data_generator.py' để sinh bộ câu hỏi.")
    else:
        print("Không lấy được dữ liệu nào.")

if __name__ == "__main__":
    run_scraper()