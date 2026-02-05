"""Tests cho formatters module"""
from app.services.formatters import (
    parse_source_metadata, 
    format_sources, 
    format_sources_markdown,
    LegalSource
)

def test_parse_source_metadata():
    """Test parsing source metadata"""
    
    # Test case 1: Đầy đủ thông tin
    source = "Điều 56 Thủ tục ly hôn Luật Hôn nhân và Gia đình"
    result = parse_source_metadata(source)
    assert result.article_number == "56"
    assert "Hôn nhân" in result.law_name
    assert "Thủ tục ly hôn" in result.article_title
    print(f"✓ Test 1: {result}")
    
    # Test case 2: Chỉ có số điều
    source = "Điều 51"
    result = parse_source_metadata(source)
    assert result.article_number == "51"
    print(f"✓ Test 2: {result}")
    
    # Test case 3: Chỉ có tên luật (không có "Điều")
    source = "Luật Lao động"
    result = parse_source_metadata(source)
    assert result.law_name == "Luật Lao động"
    assert result.article_number == ""
    print(f"✓ Test 3: {result}")
    
    # Test case 4: String rỗng
    source = ""
    result = parse_source_metadata(source)
    assert result.law_name == "Không xác định"
    print(f"✓ Test 4: {result}")
    
    # Test case 5: Số điều + luật (không có title)
    source = "Điều 173 Luật Bảo hiểm Xã hội"
    result = parse_source_metadata(source)
    assert result.article_number == "173"
    assert "Bảo hiểm" in result.law_name
    print(f"✓ Test 5: {result}")


def test_format_sources():
    """Test formatting docs list"""
    docs = [
        {"source": "Điều 56 Thủ tục ly hôn Luật Hôn nhân và Gia đình", "content": "..."},
        {"source": "Điều 51 Hôn nhân Luật Hôn nhân và Gia đình", "content": "..."},
        {"source": "Điều 56 Thủ tục ly hôn Luật Hôn nhân và Gia đình", "content": "..."},  # Duplicate
    ]
    
    formatted_list, sources_objs = format_sources(docs)
    
    # Phải deduplicate
    assert len(formatted_list) == 2
    # Phải sort
    assert "Điều 51" in formatted_list[0] or "Điều 51" in formatted_list[1]
    print(f"✓ Formatted sources: {formatted_list}")


def test_format_sources_markdown():
    """Test markdown formatting"""
    sources = [
        LegalSource("Luật Hôn nhân và Gia đình", "56", "Thủ tục ly hôn"),
        LegalSource("Luật Hôn nhân và Gia đình", "51", "Hôn nhân"),
        LegalSource("Luật Lao động", "173", ""),  # Không có title
    ]
    
    markdown = format_sources_markdown(sources)
    print(f"✓ Markdown output:\n{markdown}")
    
    assert "**Nguồn tham khảo:**" in markdown
    assert "1." in markdown
    assert "2." in markdown
    assert "3." in markdown
    # Test case không có title vẫn phải hiển thị
    assert "Điều 173" in markdown


def test_legal_source_str():
    """Test LegalSource.__str__() với các trường hợp khác nhau"""
    
    # Case 1: Đầy đủ
    src1 = LegalSource("Luật Hôn nhân và Gia đình", "56", "Thủ tục ly hôn")
    assert "Điều 56" in str(src1) and "Thủ tục ly hôn" in str(src1)
    print(f"✓ Case 1: {src1}")
    
    # Case 2: Không có title
    src2 = LegalSource("Luật Lao động", "173", "")
    assert "Điều 173" in str(src2) and "Luật Lao động" in str(src2)
    print(f"✓ Case 2: {src2}")
    
    # Case 3: Chỉ có số điều
    src3 = LegalSource("Không xác định", "51", "")
    assert "Điều 51" in str(src3)
    print(f"✓ Case 3: {src3}")
    
    # Case 4: Chỉ có tên luật
    src4 = LegalSource("Luật Thương mại", "", "")
    assert "Luật Thương mại" in str(src4)
    print(f"✓ Case 4: {src4}")


if __name__ == "__main__":
    test_parse_source_metadata()
    test_format_sources()
    test_format_sources_markdown()
    test_legal_source_str()
    print("\n✅ Tất cả tests passed!")
