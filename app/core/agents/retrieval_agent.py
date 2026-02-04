from app.core.config import client, embeddings, COLLECTION_NAME

def retriever_node(state):
    """
    Node 2+3: Retrieval Agent
    Nhiệm vụ: Thực thi việc tìm kiếm dựa trên chỉ đạo của Router.
    """
    query = state.get("standalone_query", state["query"])
    limit = state.get("search_limit", 3)
    
    if limit == 0:
        return {"retrieved_docs": []}

    print(f"🧠 [RETRIEVER]: Đang tìm {limit} văn bản...")
    
    try:
        vector = embeddings.embed_query(query)
        # Logic search Qdrant (giữ nguyên code cũ của bạn)
        try:
            results = client.search(collection_name=COLLECTION_NAME, query_vector=vector, limit=limit)
        except AttributeError:
            results = client.query_points(collection_name=COLLECTION_NAME, query=vector, limit=limit).points
            
        docs = []
        for r in results:
            payload = r.payload or {}
            docs.append({
                "source": f"{payload.get('law_name')} {payload.get('law_id', '')}",
                "content": payload.get('content', '')
            })
            
        return {"retrieved_docs": docs}
        
    except Exception as e:
        print(f"⚠️ Lỗi Retriever: {e}")
        return {"retrieved_docs": []}