from kafka import KafkaConsumer
import json
import logging

# Configurer le logging
logging.basicConfig(level=logging.INFO)

# Configuration du consommateur
kafka_topic = "weather-data"  # Assurez-vous que cela correspond au topic utilisé par le producteur
kafka_broker = "localhost:9092"  # Assurez-vous que c'est l'adresse correcte

# Créer un consommateur Kafka
consumer = KafkaConsumer(
    kafka_topic,
    bootstrap_servers=[kafka_broker],
    auto_offset_reset="latest",  # Commencer à lire depuis le début
    enable_auto_commit=True,
    group_id="weather_group",  # Identifiant du groupe de consommateurs
)

# Consommer les messages
if __name__ == "__main__":
    try:
        logging.info("En attente de nouveaux messages...")
        for message in consumer:
            try:
                # Essayer de désérialiser le message
                weather_data = json.loads(message.value.decode("utf-8"))
                logging.info(f"Reçu : {weather_data}")
            except json.JSONDecodeError as json_error:
                logging.error(
                    f"Erreur de désérialisation du message : {json_error} - Message brut : {message.value}"
                )
            except Exception as e:
                logging.error(f"Erreur lors du traitement du message : {e}")
    except KeyboardInterrupt:
        logging.info("Arrêt du consommateur.")
    except Exception as e:
        logging.error(f"Erreur lors de la consommation des messages : {e}")
    finally:
        consumer.close()
