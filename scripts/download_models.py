import os
from fastembed import TextEmbedding

def download_models():
    """Pre-download the ONNX embedding model into the Docker image."""
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    cache_dir = os.getenv("FASTEMBED_CACHE_PATH", "/app/model_cache")

    print(f"--- Downloading model: {model_name} to {cache_dir} ---")

    # Trigger download and ONNX conversion by initializing the model
    TextEmbedding(
        model_name=model_name,
        cache_dir=cache_dir,
    )

    print(f"--- Model {model_name} downloaded successfully ---")

if __name__ == "__main__":
    download_models()
