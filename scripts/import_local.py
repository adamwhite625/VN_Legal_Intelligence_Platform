import json
import os
from dotenv import load_dotenv
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter



load_dotenv()

# =============================
# CONFIG
# =============================

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "law_data")

DATA_FILE = "app/core/raw_law_data.json"

# =============================
# INIT CLIENTS
# =============================

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

print("🔄 Loading embedding model...")
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={"device": "cpu"},
)

VECTOR_SIZE = 384

# =============================
# TEXT SPLITTER (IMPORTANT)
# =============================

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
)


# =============================
# MAIN IMPORT FUNCTION
# =============================

def import_to_qdrant():

    if not os.path.exists(DATA_FILE):
        print(f"❌ File not found: {DATA_FILE}")
        return

    print(f"📖 Reading data from {DATA_FILE}...")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # Create collection if not exists
    try:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        print(f"✅ Created collection: {COLLECTION_NAME}")
    except Exception:
        print(f"ℹ️ Collection '{COLLECTION_NAME}' already exists")

    points = []
    total_chunks = 0

    print(f"🚀 Processing {len(dataset)} law articles...")

    for article in dataset:

        law_name = article.get("law_name", "")
        article_id = article.get("article_id", "")
        content = article.get("content", "")

        if not content.strip():
            continue

        # Split into chunks
        chunks = text_splitter.split_text(content)

        for chunk_index, chunk in enumerate(chunks):

            vector = embeddings_model.embed_query(chunk)

            payload = {
                # 👇 MUST MATCH retrieval_agent.py
                "so_hieu": article_id,
                "loai_van_ban": law_name,
                "page_content": chunk,
            }

            point = PointStruct(
                id=str(uuid4()),  # unique id
                vector=vector,
                payload=payload,
            )

            points.append(point)
            total_chunks += 1

            # Batch upload
            if len(points) >= 64:
                client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=points,
                )
                print(f"   -> Uploaded {total_chunks} chunks...")
                points = []

    if points:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

    print(f"\n🎉 DONE! Total chunks indexed: {total_chunks}")


if __name__ == "__main__":
    import_to_qdrant()
