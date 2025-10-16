# embeddings.py

import os
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, DATA_DIR

def load_embedding_model():
    print(f"Chargement du modèle d'embedding : {EMBEDDING_MODEL}")
    return SentenceTransformer(EMBEDDING_MODEL)

def vectorize_documents(model, collection):
    """Lit les fichiers .txt, crée les embeddings et les ajoute à Chroma."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Dossier '{DATA_DIR}' créé. Ajoute des fichiers .txt dedans.")
        return

    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]
    if not files:
        print(f"Aucun fichier .txt trouvé dans '{DATA_DIR}'")
        return

    print(f"{len(files)} fichiers trouvés dans '{DATA_DIR}'")

    for idx, filename in enumerate(files):
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        embedding = model.encode([text]).tolist()
        doc_id = f"doc_{idx}"

        collection.add(
            documents=[text],
            embeddings=embedding,
            ids=[doc_id],
            metadatas=[{"source": filename}],
        )
        print(f"Document ajouté : {filename}")

    print("\n✅ Vectorisation terminée !")
