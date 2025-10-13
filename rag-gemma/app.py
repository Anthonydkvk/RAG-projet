import os
import requests
from sentence_transformers import SentenceTransformer
from chromadb import Client
from chromadb.config import Settings

# === CONFIG ===
COLLECTION_NAME = "docs_collection"
DATA_DIR = "docs"  # dossier contenant les fichiers .txt
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:4b"  # ou "gemma:2b"

# === Connexion à ChromaDB (nouvelle version) ===
settings = Settings(
    persist_directory="./chroma_db",  # persistance sur disque (facultatif)
    anonymized_telemetry=False        # désactiver télémétrie
)
client = Client(settings=settings)

# Crée ou récupère la collection
try:
    collection = client.get_collection(COLLECTION_NAME)
    print(f"Collection '{COLLECTION_NAME}' trouvée.")
except Exception:
    collection = client.create_collection(COLLECTION_NAME)
    print(f"Nouvelle collection créée : '{COLLECTION_NAME}'")

# === Chargement du modèle d'embedding ===
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
print(f"Chargement du modèle d'embedding : {EMBEDDING_MODEL}")
model = SentenceTransformer(EMBEDDING_MODEL)

# === Menu utilisateur ===
while True:
    print("\n--- Menu ---")
    print("1. Vectoriser les documents")
    print("2. Poser une question et chercher documents")
    print("3. Poser une question à Gemma avec contexte")
    print("4. Quitter")
    choice = input("Choix : ").strip()

    if choice == "1":
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            print(f"Dossier '{DATA_DIR}' créé. Ajoute des fichiers .txt dedans.")
            continue

        files = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]
        if not files:
            print(f"Aucun fichier .txt trouvé dans '{DATA_DIR}'")
            continue

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

        print("\nVectorisation terminée !")

    elif choice == "2":
        query = input("\nPose ta question : ")
        results = collection.query(query_texts=[query], n_results=3)
        docs = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not docs:
            print("Aucun document trouvé.")
        else:
            print("\n=== Résultats similaires ===")
            for i, doc in enumerate(docs):
                print(f"\n--- Résultat {i+1} ---")
                print(doc)
                print(f"Distance : {distances[i] if i < len(distances) else 'N/A'}")

    elif choice == "3":
        query = input("\nPose ta question : ")
        results = collection.query(query_texts=[query], n_results=3)
        docs = results.get("documents", [[]])[0]

        if not docs:
            print("Aucun document trouvé pour cette question.")
            continue

        context = "\n\n".join(docs)
        prompt = f"""
Tu es un assistant utile. Réponds à la question suivante en te basant UNIQUEMENT
sur le contexte fourni.

--- CONTEXTE ---
{context}

--- QUESTION ---
{query}

Réponse :
"""

        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": True
        }, stream=True)

        print("\nRéponse :\n")
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    try:
                        data = line.decode("utf-8")
                        if '"response":"' in data:
                            text_part = data.split('"response":"')[1].split('"')[0]
                            print(text_part, end="", flush=True)
                    except Exception:
                        pass
            print("\n")
        else:
            print("Erreur lors de l'appel à Gemma :", response.text)

    elif choice == "4":
        print("Au revoir !")
        break

    else:
        print("Choix invalide. Réessaye.")
