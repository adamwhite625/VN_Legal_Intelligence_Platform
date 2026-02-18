"""
Utility functions for generating URL-friendly slugs.
Follows standard URL slugification patterns (Medium, Dev.to, etc.)
"""

import re
import unicodedata


def normalize_text(text: str) -> str:
    """
    Normalize Vietnamese text by removing accents and diacritics.
    
    Examples:
        "Điều 1" -> "Dieu 1"
        "Phạm vi" -> "Pham vi"
    """
    # Decompose Vietnamese characters
    nfd = unicodedata.normalize('NFD', text)
    # Remove combining characters (accents, diacritics)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


def generate_slug(text: str, max_length: int = 100) -> str:
    """
    Generate URL-friendly slug from text.
    
    Rules:
    - Convert to lowercase
    - Remove Vietnamese accents
    - Replace spaces and special chars with hyphens
    - Remove consecutive hyphens
    - Strip leading/trailing hyphens
    - Truncate to max_length
    
    Examples:
        "Điều 1" -> "dieu-1"
        "Điều 1 - Phạm vi điều chỉnh" -> "dieu-1-pham-vi-dieu-chinh"
        "Article #5 (Important)" -> "article-5-important"
    """
    if not text:
        return ""
    
    # Normalize Vietnamese text
    text = normalize_text(text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r'[^\w\-]', '', text)
    
    # Remove consecutive hyphens
    text = re.sub(r'-+', '-', text)
    
    # Strip leading and trailing hyphens
    text = text.strip('-')
    
    # Truncate to max_length
    if len(text) > max_length:
        text = text[:max_length].strip('-')
    
    return text


def extract_law_number(law_id: str) -> str:
    """
    Extract just the law number/article for slug.
    
    Examples:
        "Điều 1" -> "1"
        "Điều 10" -> "10" 
        "Điều 1 - Phạm vi" -> "1"
    """
    # Extract numbers from law_id
    match = re.search(r'\d+', law_id)
    return match.group(0) if match else ""


def create_law_slug(law_id: str, law_title: str = None) -> str:
    """
    Create slug for law article.
    
    Priority:
    1. If law_title provided, use descriptive slug
    2. Otherwise, create simple slug from law_id
    
    Examples:
        create_law_slug("Điều 1") -> "dieu-1"
        create_law_slug("Điều 1", "Phạm vi điều chỉnh") -> "dieu-1-pham-vi-dieu-chinh"
    """
    if law_title:
        # Combine law_id and title for descriptive slug
        combined = f"{law_id} {law_title}"
        slug = generate_slug(combined, max_length=100)
    else:
        # Simple slug from law_id only
        slug = generate_slug(law_id, max_length=50)
    
    return slug


if __name__ == "__main__":
    # Test examples
    test_cases = [
        ("Điều 1", None),
        ("Điều 1", "Phạm vi điều chỉnh"),
        ("Điều 10 - Công ty cổ phần", None),
        ("Điều 1-5", "Các định nghĩa"),
        ("Article 1 (Important)", None),
    ]
    
    print("Slug generation examples:")
    for law_id, title in test_cases:
        slug = create_law_slug(law_id, title)
        print(f"  {law_id:<30} {title or '':<30} -> {slug}")
