"""
Retriever node for Legal Agentic RAG.

Production-ready:
- Typed document output
- Score threshold
- Safe failure
"""

from app.core.config import settings
from typing import List

from app.core.clients import get_qdrant_client, get_embeddings
from app.services.law_agent.state import (
    LawAgentState,
    RetrievedDocument,
)

# Production-grade retrieval thresholds
HARD_THRESHOLD = 0.60  # Reject garbage results

# Domain filtering for all intent types
DOMAIN_KEYWORDS = {
    "SEARCH_PENAL": ["Hình sự", "Tội phạm", "Bộ luật Hình sự", "Bộ Luật Hình Sự"],
    "SEARCH_CIVIL": ["Dân sự", "Dân thiếp", "Bộ luật Dân sự", "Hợp đồng", "Bất động sản", "Bộ Luật Dân Sự"],
    "SEARCH_PROCEDURE": ["Doanh nghiệp", "Hôn nhân", "Lao động", "Thuế", "Tố tụng", "Hành chính"],
    "SEARCH_MARRIAGE": ["Hôn nhân", "Gia đình", "Hôn nhân gia đình", "Luật Hôn nhân"],
    "SEARCH_CONSULTATION": [],  # Accept all domains
    "NO_SEARCH": [],  # Accept all domains
}


def retriever_node(state: LawAgentState) -> LawAgentState:
    """
    Retrieve relevant legal documents from Qdrant.
    """

    try:
        print("\n🔍 [RETRIEVER] Starting retrieval node...")
        query = state.standalone_query or state.query
        
        # Procedural queries: limit to 3 best documents
        # Consultation queries: limit to 4
        is_procedural = state.intent == "SEARCH_PROCEDURE"
        limit = state.search_limit or (3 if is_procedural else 4)
        
        print(f"   Query: {query}")
        print(f"   Intent: {state.intent}")
        print(f"   Limit: {limit}")
        print(f"   Hard threshold: {HARD_THRESHOLD}")

        qdrant = get_qdrant_client()
        embeddings = get_embeddings()
        print("   ✓ Clients initialized")

        # Embed query
        print("   📝 Embedding query...")
        query_vector = embeddings.embed_query(query)
        print(f"   [OK] Vector dimension: {len(query_vector)}")

        # Search in Qdrant
        print(f"   🔎 Searching in Qdrant (collection: {settings.COLLECTION_NAME})...")
        results = qdrant.query_points(
    collection_name=settings.COLLECTION_NAME,
    query=query_vector,
    limit=limit,
    with_payload=True,
).points


        documents: List[RetrievedDocument] = []

        print(f"\n   Raw search results ({len(results)} hits):")
        for i, hit in enumerate(results):
            print(f"      [{i}] Score: {hit.score:.4f}")
            print(f"          Payload keys: {list(hit.payload.keys()) if hit.payload else 'None'}")
            if hit.payload:
                print(f"          so_hieu: {hit.payload.get('so_hieu', 'N/A')}")
                print(f"          loai_van_ban: {hit.payload.get('loai_van_ban', 'N/A')}")

        # Apply filtering
        filtered_results = []
        
        for hit in results:
            score = hit.score
            payload = hit.payload or {}
            loai_van_ban = payload.get("loai_van_ban", "")
            so_hieu = payload.get("so_hieu", "?")
            
            # Hard threshold only (avoid garbage)
            if score < HARD_THRESHOLD:
                print(f"      ❌ Rejected: {score:.4f} < {HARD_THRESHOLD} (garbage)")
                continue
            
            # Domain filter for all intents (get keywords from DOMAIN_KEYWORDS)
            domain_filter = DOMAIN_KEYWORDS.get(state.intent, [])
            if domain_filter and not any(keyword in loai_van_ban for keyword in domain_filter):
                print(f"      ⚠️ Filtered: '{loai_van_ban}' (wrong domain for {state.intent})")
                continue
            
            filtered_results.append(hit)
            print(f"      ✅ Kept: {score:.4f} | {so_hieu} ({loai_van_ban})")
        
        # Sort by score (should already be sorted, but ensure it)
        filtered_results.sort(key=lambda x: x.score, reverse=True)

        for hit in filtered_results:
            score = hit.score
            payload = hit.payload or {}
            
            # Extract content with fallback
            content = payload.get("page_content") or payload.get("combine_Article_Content", "")

            documents.append(
                RetrievedDocument(
                    law_id=payload.get("so_hieu", "Không rõ điều"),
                    law_name=payload.get("loai_van_ban", "Không rõ văn bản"),
                    content=content,
                    score=score,
                )
            )

        print(f"\n   📊 Final result: {len(documents)} documents after filtering (from {len(results)} initial results)")
        state.retrieved_docs = documents

        if not documents:
            print("   ⚠️ No documents found → Setting status to NO_LAW")
            state.check_status = "NO_LAW"
        else:
            print(f"   ✅ Retrieved {len(documents)} relevant documents")

        state.node_trace.append("retriever")

        return state

    except Exception as e:
        print(f"   ❌ ERROR in retriever: {str(e)}")
        import traceback
        traceback.print_exc()
        state.error_message = f"Retriever error: {str(e)}"
        state.check_status = "NO_LAW"
        return state
