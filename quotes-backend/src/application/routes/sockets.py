import json
import logging
from asyncio import sleep
from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK

from application.db.schemes import Quotes, Quote
from application.routes import PRICES
from application.core.config import settings

router = APIRouter(
    prefix="/websocket",
    tags=["websocket"],
    responses={404: {"description": "Not found"}},
)


class ConnectionManager:
    """
    Менеджер сокет соединений
    """
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    @staticmethod
    async def send(message: Quotes, websocket: WebSocket):
        # Небольшие преобразования модели для отправки полей по алиасу
        await websocket.send_json(json.loads(message.json(by_alias=True)))


manager = ConnectionManager()


@router.websocket("/open")
async def websocket_endpoint(websocket: WebSocket):
    """
    Устанавливает сокет соединение с фронтом

    Args:
        websocket: Сокет запрос

    """
    await manager.connect(websocket)
    # Приветственное сообщение от сервера
    await websocket.receive_text()

    while True:
        try:
            async with websocket.app.state.redis.client() as conn:
                # Получим значение цен из кеша или дефолтное значение
                prices: dict = await conn.hgetall("movement") or PRICES
                label: str = await conn.get("label")

            # Ожидаем интервал между отправками котировок
            await sleep(settings.quotes_interval)

            # Отправляем данные по нужной структуре
            quotes: Quotes = Quotes()
            for key, value in prices.items():
                quotes.values.append(Quote(created=label, ticker=key, price=value))

            await manager.send(quotes, websocket)

        except (WebSocketDisconnect, ConnectionClosedOK):
            manager.disconnect(websocket)
        except Exception as e:
            logging.error(f"Ошибка отправки данных {str(e)}")
            break
