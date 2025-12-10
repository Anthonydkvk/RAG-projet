# Application RAG souveraine

Ce dépôt contient une petite application RAG (Retrieval-Augmented Generation) qui utilise ChromaDB pour stocker des embeddings et un modèle (via Ollama) pour générer des réponses contextualisées.


## Aperçu rapide

- `app.py` : Interface CLI simple pour vectoriser des documents et interagir en conversation avec Gemma.
- `server.py` : API Flask qui expose des endpoints pour vectoriser, rechercher et interroger Gemma depuis une UI ou des clients externes.
- `chroma_utils.py` : Fonctions utilitaires pour créer/obtenir un client Chroma et les collections.
- `embeddings.py` : Chargement du modèle d'embeddings et logique de vectorisation des documents (supporte .txt, .md, .docx, .pdf).
- `ollama_utils.py` : Communication avec l'API Ollama (génération / chat du modèle Gemma).
- `requirements.txt` : Dépendances Python nécessaires.
- `Dockerfile` : Conteneurisation de l'application RAG (expose le serveur Flask sur le port 8000).
- `Dockerfile.ollama` : Dockerfile personnalisé pour Ollama avec le modèle gemma:2b pré-installé.
- `compose.yaml` : Configuration Docker Compose pour orchestrer l'application RAG et Ollama ensemble.
- `data/` : Contient les données et la persistance locale de Chroma (dossier `chromadb/` inclus).
- `docs/` : Documents sources (.txt, .md, .docx, .pdf) utilisés comme base de connaissances pour l'indexation.
- `web/` : Front-end statique (HTML/JS/CSS) servi par `server.py`.

## Structure des dossiers (explication)

- `app.py` — CLI pour :
  - Vectoriser les documents présents dans le dossier `docs/` (configurable via variable d'environnement `DATA_DIR`).
  - Interroger la base et afficher les documents similaires.
  - Discuter avec Gemma en mode conversation (contexte + historique).

- `server.py` — API Flask :
  - POST `/api/vectorize` : lance la vectorisation (utilise `embeddings.py` et `chroma_utils.py`).
  - POST `/api/query` : reçoit `{ "query": "...", "n_results": 3 }` et renvoie documents/distances.
  - POST `/api/ask_gemma` : reçoit `{ "query": "...", "docs": [...], "history": [...] }` et renvoie la réponse du modèle.
  - Sert aussi les fichiers statiques depuis `web/`.

- `chroma_utils.py` — Fonctions utilitaires pour créer/obtenir un client Chroma et les collections. Utilise des variables d'environnement pour la configuration (`CHROMA_DIR`, `COLLECTION_NAME`).

- `embeddings.py` — Chargement du modèle d'embeddings et logique de vectorisation des documents. 
  - Supporte les formats : .txt, .md, .docx, .pdf
  - Utilise des variables d'environnement : `EMBEDDING_MODEL`, `DATA_DIR`

- `ollama_utils.py` — Communication avec l'API Ollama (génération / chat du modèle Gemma).
  - Utilise des variables d'environnement : `OLLAMA_URL`, `MODEL_NAME`

- `Dockerfile` — Conteneurisation de l'application RAG avec build multi-stage pour optimiser la taille de l'image.

- `Dockerfile.ollama` — Dockerfile personnalisé basé sur `ollama/ollama:rocm` qui pré-installe le modèle `gemma:2b`.

- `compose.yaml` — Orchestration Docker Compose définissant deux services :
  - `ollama` : Service Ollama avec le modèle gemma:2b (port 11435:11434)
  - `rag-gemma` : Application RAG Flask (port 8000:8000)
  - Réseau partagé `rag-network` pour la communication entre services

- `data/chromadb/` — Base SQLite de Chroma si la persistance locale est utilisée. Ne pas supprimer si vous voulez garder l'index.

## Prérequis

- Python 3.11+ (le Dockerfile utilise 3.11)
- Les librairies Python nécessaires pour le fonctionnement du projet sont listées dans `requirements.txt`.
- Un service Ollama accessible (local ou via Docker Compose).
- Docker et Docker Compose (pour l'exécution conteneurisée).

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

### 1) Mode CLI (interactif)

```bash
# Lance l'interface en ligne de commande
python app.py
```

Le menu permet : vectoriser les documents (option 1), faire une recherche (option 2) ou discuter (option 3).

### 2) Mode serveur (API + front-end)

```bash
python server.py
```

- Le serveur écoute par défaut sur le port 8000 (modifiable via la variable d'environnement `PORT`).
- Ouvrez `http://localhost:8000/` pour accéder à l'interface web.

### 3) Avec Docker (image unique)

```bash
# Construire l'image
docker build -t rag-gemma:latest .

# Lancer le conteneur (expose 8000)
docker run -p 8000:8000 --name rag-gemma rag-gemma:latest
```

**Note** : Le `Dockerfile` configure par défaut `OLLAMA_URL` pour utiliser `host.docker.internal` (pratique si Ollama tourne sur l'hôte). Si Ollama est dans un autre conteneur, adaptez `OLLAMA_URL` ou utilisez Docker Compose.

### 4) Avec Docker Compose (recommandé)

Docker Compose permet de lancer l'ensemble de l'infrastructure (Ollama + RAG) avec une seule commande :

```bash

# Ou en mode détaché (en arrière-plan)
docker compose up -d --build
# Pour lance le conteneur en mode intteractif
docker compose run -it rag-gemma
```

**Services démarrés** :
- `ollama` : Service Ollama avec le modèle gemma:2b pré-installé (port 11435:11434)
- `rag-gemma` : Application RAG Flask (port 8000:8000)


## Variables d'environnement

L'application utilise des variables d'environnement (fichier `.env` ou définies directement) pour la configuration :

- `PORT` : Port sur lequel `server.py` écoute (par défaut 8000).
- `OLLAMA_URL` : URL de l'API Ollama (ex: `http://ollama:11434/api/generate` pour Docker Compose).
- `MODEL_NAME` : Nom du modèle Ollama à utiliser (ex: `gemma:2b`).
- `EMBEDDING_MODEL` : Modèle d'embedding à utiliser (ex: `sentence-transformers/all-MiniLM-L6-v2`).
- `CHROMA_DIR` : Répertoire de persistance ChromaDB (ex: `./data/chromadb`).
- `COLLECTION_NAME` : Nom de la collection ChromaDB (ex: `documents`).
- `DATA_DIR` : Dossier contenant les documents à indexer (ex: `./docs`).

Exemple pour démarrer le serveur sur le port 8080 :

```bash
python server.py
```



## Remarques et bonnes pratiques

- Sauvegardez le dossier `data/chromadb/` si vous souhaitez conserver l'index entre les sessions.
- Avec Docker Compose, les services communiquent via le réseau `rag-network`. L'application RAG accède à Ollama via `http://ollama:11434`.
- Pour Docker Compose, vous pouvez ajuster les ports dans le fichier `compose.yaml` si nécessaire.
- Les fichiers supportés pour la vectorisation sont : .txt, .md, .docx, .pdf
## Équipe

- DER KEVORKIAN Anthony
- HONG Alexis
- OUAGAGUE Loqman
- SOUIDI Chaïma



