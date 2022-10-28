import aioredis
from fastapi import FastAPI
from typing import Callable
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from application.core.config import settings


def create_start_app_handler(app: FastAPI) -> Callable:
    async def start_app() -> None:
        try:
            # Создадим подключение к БД и в state его
            app.state.db = create_async_engine(
                settings.database.engine,
                **settings.database.kwargs
            )
            app.state.session = sessionmaker(bind=app.state.db, class_=AsyncSession)
            app.state.logger.info(f"Connected to Database {settings.database.engine}")
        except ConnectionRefusedError as e:
            app.state.logging.error(f"Can't connect to Database {settings.database.engine}\n{str(e)}")
            exit(1)

        try:
            # Создадим подключение к кешу и в state его
            pool = await aioredis.from_url(
                settings.redis.engine,
                **settings.redis.kwargs
            )
            app.state.redis = pool
            app.state.logger.info(f"Connected to Redis {settings.redis.engine}")
        except ConnectionRefusedError as e:
            app.state.logger.error(f"Cannot connect to Redis {settings.redis.engine}\n{str(e)}")
            exit(1)

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        await app.state.db.dispose()
        await app.state.redis.close()

    return stop_app
