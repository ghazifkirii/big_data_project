import requests
import json
from kafka import KafkaProducer
import time
import logging

# Configurer le logging
logging.basicConfig(level=logging.INFO)

# Charger la configuration
with open("config.json", "r") as file:
    config = json.load(file)

api_key = config["api_key"]
city = config["city"]
kafka_topic = config["kafka_topic"]
kafka_broker = config["kafka_broker"]
interval = config["interval"]

# Créer un producteur Kafka
producer = KafkaProducer(
    bootstrap_servers=[kafka_broker],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)


def get_weather_data():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP

        data = response.json()
        weather_data = {
            "city": city,
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "description": data["weather"][0]["description"],
            "timestamp": int(time.time()),
        }
        return weather_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Erreur lors de la récupération des données météo: {e}")
        return None


def send_to_kafka(data):
    try:
        producer.send(kafka_topic, value=data)
        producer.flush()
        logging.info(f"Envoyé : {data}")
    except Exception as e:
        logging.error(f"Erreur d'envoi à Kafka : {e}")


# Collecter et envoyer les données en boucle
if __name__ == "__main__":
    while True:
        weather_data = get_weather_data()
        if weather_data:
            send_to_kafka(weather_data)
        time.sleep(interval)
