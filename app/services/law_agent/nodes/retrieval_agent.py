from app.core.config import client, embeddings, settings

def retriever_node(state):
    """
    Node 2: Retrieval Agent - Phiên bản "Ăn tạp" (Chấp nhận mọi loại dữ liệu)
    """
    query = state.get("standalone_query", state["query"])
    limit = state.get("search_limit", 3)
    
    if limit == 0:
        return {"retrieved_docs": []}

    print(f"🧠 [RETRIEVER]: Đang tìm {limit} văn bản cho: {query}")
    
    try:
        vector = embeddings.embed_query(query)
        
        # 1. Tìm kiếm trong Qdrant
        try:
            results = client.search(
                collection_name=settings.COLLECTION_NAME,
                query_vector=vector, 
                limit=limit
            )
        except AttributeError:
            results = client.query_points(
                collection_name=settings.COLLECTION_NAME,
                query=vector, 
                limit=limit
            ).points
            
        docs = []
        for r in results:
            payload = r.payload or {}
            
            # --- SỬA LOGIC: CHẤP NHẬN MỌI KEY (CŨ & MỚI) ---
            
            # 1. Cố gắng lấy Số hiệu (VD: Điều 51)
            # Thử tìm key 'so_hieu' (mới), nếu không có thì tìm 'law_id' (cũ), không có nữa tìm 'article_id'
            so_hieu = payload.get("so_hieu") or payload.get("law_id") or payload.get("article_id") or ""
            
            # 2. Cố gắng lấy Tên luật (VD: Luật Hôn nhân...)
            # Thử tìm 'loai_van_ban' (mới), nếu không có thì tìm 'law_name' (cũ)
            ten_luat = payload.get("loai_van_ban") or payload.get("law_name") or ""
            
            # 3. Ghép chuỗi hiển thị
            if so_hieu and ten_luat:
                source_name = f"{so_hieu} - {ten_luat}" # Chuẩn nhất
            elif so_hieu:
                source_name = so_hieu # Chỉ có điều
            elif ten_luat:
                source_name = ten_luat # Chỉ có luật
            else:
                # 4. Đường cùng: Lấy trường 'source' hoặc 'question' cũ
                source_name = payload.get("source") or payload.get("question_sample") or "Văn bản pháp luật"
            
            # Làm sạch chuỗi (xóa khoảng trắng thừa)
            source_name = str(source_name).strip()
            # -----------------------------------------------

            # Lấy nội dung (Cũng thử mọi trường có thể)
            content = (
                payload.get('combine_Article_Content') or 
                payload.get('page_content') or 
                payload.get('content') or 
                payload.get('law_content') or 
                ""
            )

            docs.append({
                "source": source_name,
                "content": content
            })
            
        return {"retrieved_docs": docs}
        
    except Exception as e:
        print(f"⚠️ Lỗi Retriever: {e}")
        return {"retrieved_docs": []}