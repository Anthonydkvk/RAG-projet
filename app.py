#app.py

from chroma_utils import get_chroma_client, get_or_create_collection
from embeddings import load_embedding_model, vectorize_documents
from ollama_utils import ask_gemma_with_context
from config import DATA_DIR

# Initialisation
client = get_chroma_client()
collection = get_or_create_collection(client)
model = load_embedding_model()

# === Menu utilisateur ===
while True:
    print("\n--- Menu ---")
    print("1. Vectoriser les documents")
    print("2. Poser une question et chercher documents")
    print("3. Poser une question à Gemma avec contexte")
    print("4. Quitter")
    choice = input("Choix : ").strip()

    if choice == "1":
        vectorize_documents(model, collection)

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
        print("\nMode discussion avec Gemma (tape écrit \"exit\" pour quitter)\n")
        history = []

        while True: 
            query = input("\nPose ta question : ")
            if query.lower() in ["exit"]:
                print("Fin de la discussion.")
                break

            results = collection.query(query_texts=[query], n_results=3)
            docs = results.get("documents", [[]])[0]
            distances = results.get("distances", [[]])[0]

            if not docs:
                print("Aucun document trouvé pour cette question.")
            else:
                print("\n=== Résultats similaires ===")
                for i, doc in enumerate(docs):
                    print(f"\n--- Résultat {i+1} ---")
                    print(doc)
                    print(f"Distance : {distances[i] if i < len(distances) else 'N/A'}")

            # Construction du prompt avec historique
            #full_prompt = ""
            #for turn in history:
            #    full_prompt += f"Utilisateur : {turn['user']}\nGemma : {turn['bot']}\n"
            #full_prompt += f"Utilisateur : {query}\nGemma :"


            response = ask_gemma_with_context(query, docs, history)

            # On ajoute à l’historique
            history.append({"user": query, "bot": response})

    elif choice == "4":
        print("Au revoir 👋")
        break

    else:
        print("Choix invalide. Réessaye.")
