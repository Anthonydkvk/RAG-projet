# --- Image de base ---
FROM python:3.11-slim

# --- Variables d'environnement ---
ENV PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# --- Dossier de travail ---
WORKDIR /rag-gemma

# --- Dépendances système ---
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential git curl && \
    rm -rf /var/lib/apt/lists/*

# --- Copier requirements et installer ---
COPY requirements.txt /rag-gemma/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir chromadb[server]==0.5.7

# --- Copier le reste du projet ---
COPY . /rag-gemma

# --- Ports exposés ---
EXPOSE 8000

# --- Commande par défaut pour lancer l'app ---
CMD ["python3", "app.py"]
