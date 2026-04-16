import os
from langchain_huggingface import HuggingFaceEmbeddings

def download_models():
    """
    Pre-download Hugging Face models to be included in the Docker image.
    This avoids slow startup times and potential timeouts on Cloud Run.
    """
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    cache_folder = os.getenv("HF_HOME", "/app/model_cache")
    
    print(f"--- Downloading model: {model_name} to {cache_folder} ---")
    
    # This will trigger the download and cache it in the specified folder
    HuggingFaceEmbeddings(
        model_name=model_name,
        cache_folder=cache_folder
    )
    
    print(f"--- Model {model_name} downloaded successfully ---")

if __name__ == "__main__":
    download_models()
