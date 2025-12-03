# embeddings.py

import os
from dotenv import load_dotenv
from docx import Document
import PyPDF2
from sentence_transformers import SentenceTransformer
#from config import EMBEDDING_MODEL, DATA_DIR
load_dotenv()
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL')
DATA_DIR = os.getenv('DATA_DIR')
def load_embedding_model():
    print(f"Chargement du modèle d'embedding : {EMBEDDING_MODEL}")
    return SentenceTransformer(EMBEDDING_MODEL) # Chargement du modèle d'embedding

def read_file_content(filepath):#retourne une chaîne de caractères
    """Lit le contenu d'un fichier selon son extension."""
    ext = os.path.splitext(filepath)[1].lower() # Obtient l'extension du fichier
    if ext in (".txt", ".md"):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read() 
    elif ext == ".docx":
        doc = Document(filepath)
        return "\n".join([p.text for p in doc.paragraphs]) # Lit le contenu des paragraphes
    elif ext == ".pdf":
        text = ""
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text
    else:
        return ""

def vectorize_documents(model, collection):# ajoute des documents vectorisés à la collection chroma
    """Lit les fichiers et crée les embeddings et les ajoute à Chroma."""
    ALLOWED_EXTENSIONS = (".txt", ".pdf", ".docx")

    if not os.path.exists(DATA_DIR):#vérifie si le dossier existe
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

    for idx, filename in enumerate(files):# idx est l'index, filename est le nom du fichier
        filepath = os.path.join(DATA_DIR, filename)
        text = read_file_content(filepath)

        if not text.strip():
            print(f"Aucun texte lisible dans : {filename}")
            continue

        embedding = model.encode([text]).tolist() # Crée l'embedding c'est une liste de liste
        doc_id = f"doc_{idx}"

        collection.add(
            documents=[text],
            embeddings=embedding,
            ids=[doc_id],
            metadatas=[{"source": filename}],
        )# Ajoute le document à la collection Chroma
        print(f"Document ajouté : {filename}")

    print("\n✅ Vectorisation terminée !")
