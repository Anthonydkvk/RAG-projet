from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from chroma_utils import get_chroma_client, get_or_create_collection
from embeddings import load_embedding_model, vectorize_documents
from ollama_utils import ask_gemma_with_context
import os

app = Flask(__name__, static_folder="web")
CORS(app)  # autorise les appels depuis ton navigateur local

# --- Initialisation RAG ---
client = get_chroma_client()
collection = get_or_create_collection(client)
model = load_embedding_model()

# === API : Vectoriser les documents ===
@app.route("/api/vectorize", methods=["POST"])
def api_vectorize():
    try:
        vectorize_documents(model, collection)
        return jsonify({"status": "Vectorisation terminée ✅"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === API : Recherche de documents ===
@app.route("/api/query", methods=["POST"])
def api_query():
    data = request.get_json()
    query = data.get("query")
    n_results = data.get("n_results", 3)

    if not query:
        return jsonify({"error": "Aucune question fournie"}), 400

    try:
        results = collection.query(query_texts=[query], n_results=n_results)
        docs = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        return jsonify({"documents": docs, "distances": distances}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === API : Poser une question à Gemma avec contexte ===
@app.route("/api/ask_gemma", methods=["POST"])
def api_ask_gemma():
    data = request.get_json()
    query = data.get("query")
    docs = data.get("docs", [])
    history = data.get("history", [])

    if not query:
        return jsonify({"error": "Question manquante"}), 400

    try:
        response = ask_gemma_with_context(query, docs, history)
        return jsonify({"response": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# === ROUTES POUR SERVIR L'INTERFACE WEB ===
@app.route("/")
def serve_index():
    return send_from_directory("web", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("web", path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
