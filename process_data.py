import json
import logging
from kafka import KafkaConsumer
from cassandra.cluster import Cluster
from config import load_config  # Importer la fonction load_config

# Configuration des logs
logging.basicConfig(level=logging.INFO)

# Charger la configuration depuis config.json
config = load_config()

# Connexion à Kafka
try:
    consumer = KafkaConsumer(
        config["kafka_topic"],  # Assurez-vous que le topic est correct
        bootstrap_servers=[config["kafka_broker"]],
        auto_offset_reset="earliest",  # Commence à consommer depuis le début si pas de commit
        group_id="weather_group",
        enable_auto_commit=True,  # Laisser Kafka gérer le commit de l'offset
        consumer_timeout_ms=1000,  # Timeout pour éviter de bloquer en cas d'absence de messages
    )
    logging.info("Connexion à Kafka réussie")
except Exception as e:
    logging.error(f"Échec de la connexion à Kafka: {e}")
    exit(1)  # Quitter si la connexion échoue

# Connexion à Cassandra
try:
    cluster = Cluster([config["cassandra_host"]])  # Connexion au conteneur Cassandra
    session = cluster.connect(
        config["cassandra_keyspace"]
    )  # Assurez-vous que le keyspace existe
    logging.info("Connexion à Cassandra réussie")
except Exception as e:
    logging.error(f"Erreur lors de la connexion à Cassandra: {e}")
    exit(1)


# Fonction pour insérer dans Cassandra avec vérification
def insert_into_cassandra(data):
    try:
        query = """
        INSERT INTO weather_data (timestamp, temperature, humidity, pressure)
        VALUES (%s, %s, %s, %s)
        """
        session.execute(
            query,
            (
                data["timestamp"],
                data["temperature"],
                data["humidity"],
                data["pressure"],
            ),
        )
        logging.info(f"Données insérées : {data}")

        # Vérification après insertion
        check_query = "SELECT COUNT(*) FROM weather_data"
        count = session.execute(check_query).one()[0]
        logging.info(f"Total records in weather_data: {count}")

    except Exception as e:
        logging.error(f"Erreur lors de l'insertion des données dans Cassandra : {e}")


# Consommer les messages Kafka et insérer dans Cassandra
if __name__ == "__main__":
    try:
        logging.info("Démarrage de la consommation des messages...")
        for message in consumer:
            try:
                # Désérialiser le message Kafka
                weather_data = json.loads(message.value.decode("utf-8"))
                logging.info(f"Message reçu : {weather_data}")

                # Insérer dans Cassandra
                insert_into_cassandra(weather_data)
            except json.JSONDecodeError as e:
                logging.error(f"Erreur de désérialisation du message : {e}")
            except Exception as e:
                logging.error(f"Erreur lors du traitement du message : {e}")
    except KeyboardInterrupt:
        logging.info("Arrêt du consommateur...")
    except Exception as e:
        logging.error(f"Erreur générale lors de la consommation : {e}")
    finally:
        logging.info("Fermeture des connexions...")
        consumer.close()
        session.shutdown()
        cluster.shutdown()


# import json
# from kafka import KafkaConsumer
# from cassandra.cluster import Cluster
# import logging

# # Configuration des logs
# logging.basicConfig(level=logging.INFO)

# # Connexion à Kafka
# consumer = KafkaConsumer(
#     "weather-data",  # Assurez-vous que c'est le bon topic
#     bootstrap_servers=["kafka:9092"],
#     auto_offset_reset="earliest",
#     group_id="weather_group",
# )

# # Connexion à Cassandra
# cluster = Cluster(["cassandra"])  # Connexion au conteneur Cassandra
# session = cluster.connect("weather")  # Assurez-vous que le keyspace existe


# # Fonction pour insérer dans Cassandra
# def insert_into_cassandra(data):
#     try:
#         query = "INSERT INTO weather_data (timestamp, temperature, humidity, pressure) VALUES (%s, %s, %s, %s)"
#         session.execute(
#             query,
#             (
#                 data["timestamp"],
#                 data["temperature"],
#                 data["humidity"],
#                 data["pressure"],
#             ),
#         )
#         logging.info(f"Inserted data: {data}")
#     except Exception as e:
#         logging.error(f"Error inserting data into Cassandra: {e}")


# # Consommer les messages Kafka et insérer dans Cassandra
# if __name__ == "__main__":
#     try:
#         for message in consumer:
#             try:
#                 # Désérialiser le message Kafka
#                 weather_data = json.loads(message.value.decode("utf-8"))
#                 logging.info(f"Received data: {weather_data}")

#                 # Insérer dans Cassandra
#                 insert_into_cassandra(weather_data)
#             except json.JSONDecodeError as e:
#                 logging.error(f"Error decoding JSON: {e}")
#             except Exception as e:
#                 logging.error(f"Error processing message: {e}")
#     except KeyboardInterrupt:
#         logging.info("Shutting down the consumer...")
#     finally:
#         consumer.close()
#         session.shutdown()
#         cluster.shutdown()
