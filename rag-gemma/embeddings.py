# embeddings.py

import os
from docx import Document
import PyPDF2
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, DATA_DIR

def load_embedding_model():
    print(f"Chargement du modèle d'embedding : {EMBEDDING_MODEL}")
    return SentenceTransformer(EMBEDDING_MODEL)

def read_file_content(filepath):
    """Lit le contenu d'un fichier selon son extension."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in (".txt", ".md"):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".docx":
        doc = Document(filepath)
        return "\n".join([p.text for p in doc.paragraphs])
    elif ext == ".pdf":
        text = ""
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text
    else:
        return ""

def vectorize_documents(model, collection):
    """Lit les fichiers et crée les embeddings et les ajoute à Chroma."""
    ALLOWED_EXTENSIONS = (".txt", ".pdf", ".docx")

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Dossier '{DATA_DIR}' créé. Ajoute des fichiers {ALLOWED_EXTENSIONS} dedans.")
        return

    files = [
        f for f in os.listdir(DATA_DIR)
        if f.lower().endswith(ALLOWED_EXTENSIONS)
    ]

    if not files:
        print(f"Aucun fichier {ALLOWED_EXTENSIONS} trouvé dans '{DATA_DIR}'")
        return

    print(f"{len(files)} fichiers trouvés dans '{DATA_DIR}' : {files}")

    for idx, filename in enumerate(files):
        filepath = os.path.join(DATA_DIR, filename)
        text = read_file_content(filepath)

        if not text.strip():
            print(f"Aucun texte lisible dans : {filename}")
            continue

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
