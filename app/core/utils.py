import re

def extract_keywords(text: str):
    """Tách từ khóa cơ bản từ câu truy vấn"""
    # Loại bỏ ký tự đặc biệt trừ gạch chéo và gạch ngang (thường có trong số hiệu luật)
    text = re.sub(r'[^\w\s/-]', '', text)
    words = text.split()
    unique_words = list(dict.fromkeys(words)) # Loại bỏ từ trùng lặp
    return unique_words

def process_keywords(keywords: list):
    """Xử lý từ khóa: giữ nguyên số La Mã, còn lại chuyển thường"""
    result = []
    # Regex nhận diện số La Mã (I, II, IV, X...)
    roman_numeral_pattern = re.compile(r"^(?=[MDCLXVI])M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$")
    
    for word in keywords:
        if roman_numeral_pattern.match(word) or any(c in word for c in "/-"):
            result.append(word)
        else:
            result.append(word.lower())
    return result

def format_docs_for_context(documents: list):
    """Chuyển danh sách docs tìm được thành chuỗi văn bản để đưa vào Prompt"""
    formatted_docs = []
    for doc in documents:
        # Giả sử doc là object có payload (metadata) và page_content
        content = doc.payload.get("combine_Article_Content", "")
        # Nếu không có combine content thì lấy content thường
        if not content:
            content = doc.payload.get("page_content", "")
            
        formatted_docs.append(content)
    
    return "\n\n<=-=-=-=-=>\n\n".join(formatted_docs)