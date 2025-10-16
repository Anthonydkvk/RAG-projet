# ollama_utils.py

import requests
from config import OLLAMA_URL, MODEL_NAME

def ask_gemma_with_context(query, docs):
    """Pose une question à Gemma avec un contexte fourni."""
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
        print("❌ Erreur lors de l'appel à Gemma :", response.text)
