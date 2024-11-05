import json
import os


def load_config(config_path="config.json"):
    """Charge la configuration depuis un fichier JSON."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Le fichier de configuration {config_path} est introuvable."
        )

    with open(config_path, "r") as file:
        config = json.load(file)

    return config
