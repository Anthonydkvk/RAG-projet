# ollama_utils.py

import requests
from config import OLLAMA_URL, MODEL_NAME

def ask_gemma_with_context(query, docs, history=None):
    """Pose une question à Gemma avec un contexte fourni."""
    context = "\n\n".join(docs) # Concatène les documents avec des sauts de ligne

    # Formatage lisible de l’historique
    dialogue = ""
    if history:
        #for turn in history[-5:]:  # on garde les 5 derniers tours
        for turn in history:  # on considère tout l'historique
            dialogue += f"Utilisateur : {turn['user']}\nGemma : {turn['bot']}\n"


    prompt = f"""
Tu es Gemma, une assistante IA utile et amicale. 
Réponds à l'utilisateur en te basant sur le contexte fourni ET sur la conversation précédente.

--- CONTEXTE DOCUMENTAIRE ---
{context}

--- CONVERSATION PRÉCÉDENTE ---
{dialogue}

--- NOUVELLE QUESTION ---
Utilisateur : {query}

Gemma :
"""

    response = requests.post(OLLAMA_URL, json={"model": MODEL_NAME,"prompt": prompt,"stream": True}, stream=True)
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
        return response.iter_lines()
    else:
        print("❌ Erreur lors de l'appel à Gemma :", response.text)
        return None