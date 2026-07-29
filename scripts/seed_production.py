#!/usr/bin/env python3
"""
One-time seed script for production deployment.

Creates MySQL tables and imports law data into Qdrant.
Designed to run as an ECS task after infrastructure is provisioned.
"""

import os
import sys
import time
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def wait_for_mysql(max_retries=30, delay=5):
    """Wait until MySQL is accepting connections."""
    import pymysql

    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", 3306))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "law_chatbot_db")

    for attempt in range(max_retries):
        try:
            conn = pymysql.connect(host=host, port=port, user=user, password=password)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
            conn.close()
            logger.info("MySQL is ready at %s:%d", host, port)
            return True
        except Exception as e:
            logger.warning("MySQL attempt %d/%d: %s", attempt + 1, max_retries, str(e))
            time.sleep(delay)

    logger.error("MySQL did not become available after %d attempts", max_retries)
    return False


def create_tables():
    """Create all SQLAlchemy-managed tables."""
    from app.db.session import engine, Base
    from app.models import User, ChatSession, Message, SavedLaw, SavedQuestion, MessageSummary

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("All tables created successfully")


def wait_for_qdrant(max_retries=30, delay=5):
    """Wait until Qdrant is accepting connections."""
    from qdrant_client import QdrantClient

    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", 6333))

    for attempt in range(max_retries):
        try:
            client = QdrantClient(host=host, port=port, timeout=5.0)
            client.get_collections()
            logger.info("Qdrant is ready at %s:%d", host, port)
            return True
        except Exception as e:
            logger.warning("Qdrant attempt %d/%d: %s", attempt + 1, max_retries, str(e))
            time.sleep(delay)

    logger.error("Qdrant did not become available after %d attempts", max_retries)
    return False


def seed_qdrant():
    """Import law data into Qdrant vector database."""
    from uuid import uuid4
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct, VectorParams, Distance
    from langchain_community.embeddings import FastEmbedEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", 6333))
    collection_name = os.getenv("COLLECTION_NAME", "law_data")
    data_file = os.path.join(os.path.dirname(__file__), "..", "data", "raw_law_data.json")

    if not os.path.exists(data_file):
        logger.error("Data file not found: %s", data_file)
        return False

    client = QdrantClient(host=host, port=port, timeout=30.0)

    # Check if collection already has data (skip if seeded)
    try:
        info = client.get_collection(collection_name)
        if info.points_count and info.points_count > 0:
            logger.info("Collection '%s' already has %d points, skipping seed", collection_name, info.points_count)
            return True
    except Exception:
        pass

    logger.info("Loading embedding model...")
    embeddings_model = FastEmbedEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    # Determine vector size from a test embedding
    test_vector = embeddings_model.embed_query("test")
    vector_size = len(test_vector)
    logger.info("Vector size: %d", vector_size)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

    # Create collection
    try:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        logger.info("Created collection: %s", collection_name)
    except Exception:
        logger.info("Collection '%s' already exists", collection_name)

    with open(data_file, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    logger.info("Processing %d law articles...", len(dataset))

    points = []
    total_chunks = 0

    for article in dataset:
        law_name = article.get("law_name", "")
        article_id = article.get("article_id", "")
        content = article.get("content", "")

        if not content.strip():
            continue

        chunks = text_splitter.split_text(content)

        for chunk in chunks:
            vector = embeddings_model.embed_query(chunk)

            payload = {
                "so_hieu": article_id,
                "loai_van_ban": law_name,
                "page_content": chunk,
            }

            points.append(PointStruct(id=str(uuid4()), vector=vector, payload=payload))
            total_chunks += 1

            if len(points) >= 64:
                client.upsert(collection_name=collection_name, points=points)
                logger.info("Uploaded %d chunks...", total_chunks)
                points = []

    if points:
        client.upsert(collection_name=collection_name, points=points)

    logger.info("Seed complete. Total chunks indexed: %d", total_chunks)
    return True


def main():
    """Run the full seeding pipeline."""
    logger.info("Starting production seed...")

    if not wait_for_mysql():
        sys.exit(1)

    create_tables()

    if not wait_for_qdrant():
        sys.exit(1)

    if not seed_qdrant():
        sys.exit(1)

    logger.info("All seeding completed successfully")


if __name__ == "__main__":
    main()
