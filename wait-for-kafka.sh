#!/bin/bash
# Script pour attendre que Kafka soit prêt avant de démarrer le traitement

# Attendre que Kafka soit prêt
until nc -z kafka 9092; do
  echo "Attente de Kafka..."
  sleep 3
done

echo "Kafka est prêt, lancement du script Python."
exec "$@"
