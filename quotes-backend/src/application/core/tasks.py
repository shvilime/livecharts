import logging

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
    """ Задание генерит набор изменений котировок и отправляет его в БД """
    for key, value in MOVEMENTS.items():
        MOVEMENTS[key] = generate_movement()
    try:
        requests.put(
            f"http://{settings.host}/api/quotes/movement",
            headers={'Content-Type': 'application/json'},
            json=MOVEMENTS,
            timeout=1,
        )
    except (HTTPError, Timeout):
        logging.error("Ошибка обновления котировок")


def calc_decimation():
    """ Задание инициирует пересчет исторических графиков """
    try:
        requests.get(
            f"http://{settings.host}/api/quotes/decimation",
            headers={'Content-Type': 'application/json'},
            timeout=1,
        )
    except HTTPError:
        logging.error("Ошибка запуска пересчета")
    except Timeout:
        pass
