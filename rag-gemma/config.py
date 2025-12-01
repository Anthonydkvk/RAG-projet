# config.py

COLLECTION_NAME = "docs_collection"
DATA_DIR = "docs"  # dossier contenant les fichiers .txt
OLLAMA_URL = "http://localhost:11434/api/generate"
#OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
MODEL_NAME = "gemma3:4b"  # ou "gemma:2b"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_DIR = "./chroma_db"
