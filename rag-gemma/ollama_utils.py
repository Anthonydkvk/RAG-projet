# ollama_utils.py

import requests
from config import OLLAMA_URL, MODEL_NAME

def ask_gemma_with_context(query, docs, history=None):
    context = "\n\n".join(docs)

    dialogue = ""
    if history:
        for turn in history:
            dialogue += f"Utilisateur : {turn['user']}\nGemma : {turn['bot']}\n"

    prompt = f"""
--- CONTEXTE ---
{context}

--- CONVERSATION ---
{dialogue}

--- QUESTION ---
{query}

Réponse :
"""

    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL_NAME, "prompt": prompt, "stream": True},
        stream=True
    )

    full_text = ""

    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                try:
                    data = line.decode("utf-8")
                    if '"response":"' in data:
                        part = data.split('"response":"')[1].split('"')[0]
                        full_text += part
                except:
                    pass
        print(full_text)
        return full_text
    else:
        print("Erreur", response.text)
        return "Erreur : impossible d’obtenir la réponse"
