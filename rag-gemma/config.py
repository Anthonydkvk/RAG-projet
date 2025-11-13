# config.py

COLLECTION_NAME = "docs_collection" # nom de la collection Chroma
DATA_DIR = "docs"  # dossier contenant les fichiers .txt à vectoriser
#OLLAMA_URL = "http://localhost:11434/api/generate" # URL de l'API Ollama
OLLAMA_URL = "http://host.docker.internal:11434/api/generate" # URL de l'API Ollama pour Docker
MODEL_NAME = "gemma3:4b"  # ou "gemma:2b"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2" # modèle d'embedding
CHROMA_DIR = "./chroma_db" # répertoire de persistance Chroma
