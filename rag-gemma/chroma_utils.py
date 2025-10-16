# chroma_utils.py

from chromadb import Client
from chromadb.config import Settings
from config import CHROMA_DIR, COLLECTION_NAME

def get_chroma_client():
    """Initialise et retourne un client Chroma."""
    settings = Settings(
        persist_directory=CHROMA_DIR,
        anonymized_telemetry=False
    )
    return Client(settings=settings)

def get_or_create_collection(client):
    """Récupère la collection si elle existe, sinon la crée."""
    try:
        collection = client.get_collection(COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' trouvée.")
    except Exception:
        collection = client.create_collection(COLLECTION_NAME)
        print(f"Nouvelle collection créée : '{COLLECTION_NAME}'")
    return collection
