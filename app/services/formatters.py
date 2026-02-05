"""Utility để format dữ liệu tham khảo và nguồn pháp lý"""
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class LegalSource:
    """Lớp để lưu metadata của một nguồn pháp lý"""
    law_name: str          # Tên luật (VD: "Luật Hôn nhân và Gia đình")
    article_number: str    # Số điều (VD: "56")
    article_title: str = "" # Tiêu đề điều (VD: "Thủ tục ly hôn")
    
    def __str__(self) -> str:
        """
        Format tùy theo thông tin có sẵn:
        - Đầy đủ: Điều 56 - Thủ tục ly hôn (Luật Hôn nhân và Gia đình)
        - Không có title: Điều 56 (Luật Hôn nhân và Gia đình)
        - Chỉ có số: Điều 56
        - Chỉ có luật: Luật Hôn nhân và Gia đình
        """
        parts = []
        
        # Phần 1: Số điều
        if self.article_number:
            parts.append(f"Điều {self.article_number}")
        
        # Phần 2: Tiêu đề (nếu có)
        if self.article_title:
            parts.append(f"- {self.article_title}")
        
        # Kết hợp phần 1 + 2
        main_part = " ".join(parts) if parts else ""
        
        # Phần 3: Tên luật (trong dấu ngoặc)
        if self.law_name and self.law_name != "Không xác định":
            if main_part:
                return f"{main_part} ({self.law_name})"
            else:
                return self.law_name
        else:
            # Nếu không có tên luật, trả về chỉ phần 1+2 hoặc fallback
            return main_part if main_part else "Không xác định"
    
    def __eq__(self, other):
        """So sánh dựa trên law_name + article_number"""
        if not isinstance(other, LegalSource):
            return False
        return (self.law_name == other.law_name and 
                self.article_number == other.article_number)
    
    def __hash__(self):
        """Cho phép dùng trong set"""
        return hash((self.law_name, self.article_number))


def extract_article_number(text: str) -> str:
    """
    Trích xuất số điều từ chuỗi
    VD: "Điều 56 Thủ tục" -> "56"
    """
    match = re.search(r'Điều\s*(\d+)', text)
    return match.group(1) if match else ""


def normalize_law_name(text: str) -> str:
    """
    Chuẩn hóa tên luật
    VD: "Luật  Hôn nhân  gia đình" -> "Luật Hôn nhân và Gia đình"
    """
    # Loại bỏ spaces thừa
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Các mapping để chuẩn hóa tên luật phổ biến
    normalizations = {
        r"Luật\s+hôn nhân\s+[và|&]?\s*gia đình": "Luật Hôn nhân và Gia đình",
        r"Luật\s+lao động": "Luật Lao động",
        r"Bộ\s+luật\s+dân\s+sự": "Bộ Luật Dân sự",
        r"Bộ\s+luật\s+hình\s+sự": "Bộ Luật Hình sự",
    }
    
    for pattern, replacement in normalizations.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


def parse_source_metadata(source_str: str) -> LegalSource:
    """
    Parse source string thành LegalSource
    
    Các định dạng hỗ trợ:
    - "Điều 56 Thủ tục ly hôn Luật Hôn nhân và Gia đình"
    - "Điều 51"
    - "Luật Hôn nhân và Gia đình"
    - Hoặc gần như bất kỳ định dạng nào
    """
    if not source_str:
        return LegalSource(law_name="Không xác định", article_number="")
    
    source_str = source_str.strip()
    
    # Tách các phần chính
    # Ưu tiên tìm "Điều X" đầu tiên
    article_num = extract_article_number(source_str)
    
    # Tìm tên luật (thường nằm sau "Luật" hoặc ở cuối)
    law_match = re.search(
        r'(?:Luật|Bộ Luật|Law)[\s\w\u0100-\uffff&và]+',
        source_str,
        re.IGNORECASE
    )
    
    if law_match:
        law_name = normalize_law_name(law_match.group(0))
    else:
        # Nếu không tìm thấy từ khóa "Luật", lấy toàn bộ string làm tên luật
        # Loại bỏ phần "Điều X" đã lấy
        if article_num:
            law_name = re.sub(rf'Điều\s*{article_num}\s*', '', source_str).strip()
        else:
            law_name = source_str.strip()
        
        # Nếu vẫn rỗng, dùng fallback
        if not law_name:
            law_name = "Không xác định"
    
    # Trích xuất tiêu đề điều (nếu có)
    # Thường nằm giữa số điều và tên luật
    article_title = ""
    if article_num:
        # Tìm text sau "Điều X" nhưng trước "Luật" hoặc ở cuối
        pattern = rf'Điều\s*{article_num}\s*[-–]?\s*(.*?)(?:Luật|Bộ|$)'
        match = re.search(pattern, source_str, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Lọc bỏ những string ngắn không phải tiêu đề (VD: số điều khác)
            if title and not re.match(r'^\d+', title):
                article_title = title
    
    return LegalSource(
        law_name=law_name if law_name else "Không xác định",
        article_number=article_num,
        article_title=article_title
    )


def format_sources(docs: List[Dict]) -> Tuple[List[str], List[LegalSource]]:
    """
    Format danh sách documents thành sources sạch
    
    Args:
        docs: Danh sách dict với key 'source' và 'content'
    
    Returns:
        (formatted_sources_list, legal_sources_objects)
    """
    unique_sources = {}  # key: (law_name, article_number), value: LegalSource
    
    for doc in docs:
        source_str = doc.get("source", "")
        if not source_str:
            continue
        
        legal_source = parse_source_metadata(source_str)
        
        # Deduplicate dựa trên law_name + article_number
        key = (legal_source.law_name, legal_source.article_number)
        if key not in unique_sources:
            unique_sources[key] = legal_source
    
    # Sort: theo tên luật, rồi theo số điều
    sorted_sources = sorted(
        unique_sources.values(),
        key=lambda x: (x.law_name, int(x.article_number) if x.article_number.isdigit() else 0)
    )
    
    formatted_list = [str(src) for src in sorted_sources]
    
    return formatted_list, sorted_sources


def format_sources_markdown(sources: List[LegalSource]) -> str:
    """
    Format sources thành markdown
    
    Output:
    ```
    **Nguồn tham khảo:**
    1. Điều 56 - Thủ tục ly hôn (Luật Hôn nhân và Gia đình)
    2. Điều 51 - Hôn nhân (Luật Hôn nhân và Gia đình)
    ```
    """
    if not sources:
        return "Không có nguồn tham khảo"
    
    lines = ["**Nguồn tham khảo:**"]
    for i, source in enumerate(sources, 1):
        lines.append(f"{i}. {str(source)}")
    
    return "\n".join(lines)


def format_context_with_sources(docs: List[Dict]) -> str:
    """
    Format context text từ documents với source rõ ràng
    """
    formatted_parts = []
    
    for i, doc in enumerate(docs, 1):
        source = doc.get("source", "Không xác định")
        legal_source = parse_source_metadata(source)
        content = doc.get("content", "").strip()
        
        part = f"""
**Tài liệu {i}: {str(legal_source)}**
{content}
"""
        formatted_parts.append(part)
    
    return "\n".join(formatted_parts)
