# Utiliser une image Python 3.9 basée sur Debian (plus légère)
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances et installer les paquets nécessaires
COPY requirements.txt ./

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Installer netcat pour attendre la disponibilité de Kafka et Cassandra
RUN apt-get update && apt-get install -y --no-install-recommends netcat && rm -rf /var/lib/apt/lists/*

# Copier tout le code source dans le conteneur
COPY . .

# Copier le script d'attente et le rendre exécutable
COPY wait-for-kafka.sh /usr/local/bin/wait-for-kafka.sh
RUN chmod +x /usr/local/bin/wait-for-kafka.sh

# Définir la commande d'entrée pour attendre Kafka et lancer le script Python
CMD ["wait-for-kafka.sh", "python", "process_data.py"]
