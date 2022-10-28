import requests
from random import random
from requests.exceptions import HTTPError, Timeout

from application.core.config import settings

# Словарик, для генерации изменений в ценах
MOVEMENTS: dict = dict.fromkeys([f"ticker_{str(i).zfill(2)}" for i in range(0, 100)])


def generate_movement():
    movement = -1 if random() < 0.5 else 1
    return movement


def generate_quotes():
    for key, value in MOVEMENTS.items():
        MOVEMENTS[key] = generate_movement()
    try:
        requests.put(
            f"http://{settings.host}:{settings.port}/quotes/movement",
            headers={'Content-Type': 'application/json'},
            json=MOVEMENTS,
            timeout=1,
        )
    except (HTTPError, Timeout):
        pass
