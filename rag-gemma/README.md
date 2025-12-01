# Application RAG souveraine

Ce dépôt contient une petite application RAG (Retrieval-Augmented Generation) qui utilise ChromaDB pour stocker des embeddings et un modèle (via Ollama) pour générer des réponses contextualisées.


## Aperçu rapide

- `app.py` : Interface CLI simple pour vectoriser des documents et interagir en conversation avec Gemma.
- `server.py` : API Flask qui expose des endpoints pour vectoriser, rechercher et interroger Gemma depuis une UI ou des clients externes.
- `config.py` : Paramètres de configuration (chemins, URL d'Ollama, noms de modèles, etc.).
- `requirements.txt` : Dépendances Python nécessaires.
- `Dockerfile` : Conteneurisation de l'application (expose le serveur Flask sur le port 8000).
- `data/` : Contient les données et la persistance locale de Chroma (dossier `chromadb/` inclus).
- `docs/` : Documents sources (.txt) utilisés comme base de connaissances pour l'indexation.
- `web/` : Front-end statique (HTML/JS/CSS) servi par `server.py`.

## Structure des dossiers (explication)

- `app.py` — CLI pour :
  - Vectoriser les documents présents dans `config.DATA_DIR` (par défaut `docs/`).
  - Interroger la base et afficher les documents similaires.
  - Discuter avec Gemma en mode conversation (contexte + historique).

- `server.py` — API Flask :
  - POST `/api/vectorize` : lance la vectorisation (utilise `embeddings.py` et `chroma_utils.py`).
  - POST `/api/query` : reçoit `{ "query": "...", "n_results": 3 }` et renvoie documents/distances.
  - POST `/api/ask_gemma` : reçoit `{ "query": "...", "docs": [...], "history": [...] }` et renvoie la réponse du modèle.
  - Sert aussi les fichiers statiques depuis `web/`.

- `chroma_utils.py` — Fonctions utilitaires pour créer/obtenir un client Chroma et les collections.
- `embeddings.py` — Chargement du modèle d'embeddings et logique de vectorisation des documents.
- `ollama_utils.py` — Communication avec l'API Ollama (génération / chat du modèle Gemma).
- `config.py` — Valeurs modifiables :
  - `COLLECTION_NAME` — nom de la collection Chroma utilisée.
  - `DATA_DIR` — dossier où sont les fichiers à indexer (par défaut `docs`).
  - `OLLAMA_URL` — URL de l'API Ollama (par défaut `http://host.docker.internal:11434/api/generate` pour Docker).
  - `MODEL_NAME` — nom du modèle Ollama (ex: `gemma3:4b`).
  - `EMBEDDING_MODEL` — identifiant du modèle d'embedding (ex: `sentence-transformers/all-MiniLM-L6-v2`).
  - `CHROMA_DIR` — répertoire de persistance Chroma (`./chroma_db` par défaut).

- `data/chromadb/` — Base SQLite de Chroma si la persistance locale est utilisée. Ne pas supprimer si vous voulez garder l'index.

## Prérequis

- Python 3.11+ (le Dockerfile utilise 3.11, l'environnement virtuel dans le repo cible Python 3.12)
- Les libraies python nécessaires pour le fonctionnement du projet sont listés dans `requirements.txt`.
- Un service Ollama accessible si vous utilisez le modèle local via Ollama (voir `OLLAMA_URL` dans `config.py`).

## Installation locale

Ouvrez un terminal à la racine du projet :

```bash
# Créer un environnement virtuel (ou activer l'environnement fourni `rag-env`)
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

```


## Lancer l'application

1) Mode CLI (interactif)

Dans le fichier config.py, il faut définir OLLAMA_URL = "http://localhost:11434/api/generate" :

OLLAMA_URL = "http://localhost:11434/api/generate" # pour tourner en local
#OLLAMA_URL = "http://host.docker.internal:11434/api/generate" # pour Docker

Ensuite :
```bash
# Lance l'interface en ligne de commande
python app.py
```

Le menu permet : vectoriser les documents (option 1), faire une recherche (option 2) ou discuter (option 3).

En plus : Mode serveur (API + front-end)

```bash
python server.py
```

- Le serveur écoute par défaut sur le port 8000 (modifiable via la variable d'environnement `PORT`).
- Ouvrez `http://localhost:8000/` pour accéder à l'interface web.

2) Avec Docker

Dans le fichier config.py, il faut définir OLLAMA_URL = "http://host.docker.internal:11434/api/generate" :

#OLLAMA_URL = "http://localhost:11434/api/generate" # pour tourner en local
OLLAMA_URL = "http://host.docker.internal:11434/api/generate" # pour Docker

Ensuite :
```bash
# Construire l'image
docker build -t rag-gemma:latest .

# Lancer le conteneur (expose 8000)
docker run -p 8000:8000 --name rag-gemma rag-gemma:latest
```

Note : Le `Dockerfile` configure par défaut `OLLAMA_URL` pour utiliser `host.docker.internal` (pratique si Ollama tourne sur l'hôte). Si Ollama est dans un autre conteneur, adaptez `OLLAMA_URL` ou utilisez un réseau Docker partagé.

## Variables d'environnement utiles

- `PORT` : port sur lequel `server.py` écoute (par défaut 8000).
- `OLLAMA_URL` : URL de l'API Ollama si vous voulez pointer vers un autre host.
- `CHROMA_DIR` : dossier de persistance Chroma si vous changez l'emplacement.

Exemple pour démarrer le serveur sur le port 8080 :

```bash
export PORT=8080
python server.py
```

## Endpoints API (exemples curl)

- Vectoriser (POST) :

```bash
curl -X POST http://localhost:8000/api/vectorize
```

- Requête simple (POST) :

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Qui a écrit le document X?", "n_results": 3}'
```

- Poser une question à Gemma (POST) :

```bash
curl -X POST http://localhost:8000/api/ask_gemma \
  -H "Content-Type: application/json" \
  -d '{"query":"Quelle est la synthèse de ce document ?", "docs": ["texte1...", "texte2..."], "history": []}'
```

## Remarques et bonnes pratiques

- Sauvegardez le dossier `data/chromadb/` ou `CHROMA_DIR` si vous souhaitez conserver l'index entre les sessions.
- Vérifiez que l'API Ollama est accessible à l'URL définie dans `config.py` avant d'utiliser les endpoints qui appellent `ollama_utils`.
- Les modèles d'embeddings et les modèles Ollama peuvent nécessiter du CPU/GPU et du temps pour la génération/chargement : prévoyez des ressources suffisantes.
## Équipe

- DER KEVORKIAN Anthony
- HONG Alexis
- OUAGAGUE Loqman
- SOUIDI Chaïma



