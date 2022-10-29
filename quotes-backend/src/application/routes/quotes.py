import numpy as np
from scipy import signal
from http import HTTPStatus
from typing import Optional
from datetime import datetime

from sqlalchemy.engine import Result
from sqlalchemy import insert, select, text
from fastapi import APIRouter, Request, Body, HTTPException

from application.routes import PRICES, DATE_FORMAT
from application.db.schemes import QuoteScheme, Quotes, Quote

router = APIRouter(
    prefix="/quotes",
    tags=["quotes"],
    responses={404: {"description": "Not found"}},
)


@router.put("/movement")
async def update_prices(r: Request, movements: dict = Body(...)):
    """
    Обновляет цены в кеше и БД исходя из поступивших изменений

    Args:
        r: Запрос
        movements: Словарь с изменениями цен по каждому тикеру

    """
    # Время обновления цен
    created: datetime = datetime.now().replace(microsecond=0)
    r.app.state.logger.debug(f"Запрос на изменения цен {movements}")

    # Обновим цены в кеше
    async with r.app.state.redis.client() as conn:
        # Получим значение цен из кеша или дефолтное значение
        prices: dict = await conn.hgetall("movement") or PRICES
        # Сложим цены и пришедшие изменения
        for key in prices.keys():
            prices[key] = int(prices[key]) + movements[key]
        r.app.state.logger.debug(f"Цены после изменения {prices}")

        # Запишем актуальные цены в кеш
        await conn.hset("movement", mapping=prices)
        await conn.set("label", created.strftime(DATE_FORMAT))
        r.app.state.logger.debug("Цены записаны в кеш")

    # Запишем цены в БД
    async with r.app.state.session() as session:
        bulk: list = []
        for key in prices.keys():
            bulk.append({"created": created, "ticker": key, "movement": movements[key], "price": prices[key]})
        await session.execute(insert(QuoteScheme, bulk))
        await session.commit()
        r.app.state.logger.debug("Цены записаны в БД")

    return {"result": "OK"}


@router.get("/current/{ticker}")
async def get_current_prices(r: Request, ticker: Optional[str] = None):
    """
    Возвращает текуще цены из кеша

    Args:
        r: Запрос
        ticker: Тикер. Если не указан, то по всем тикерам

    Returns:
        Текущие цены

    """
    async with r.app.state.redis.client() as conn:
        # Получим значение цен из кеша или дефолтное значение
        prices: dict = await conn.hgetall("movement") or PRICES
        for key in prices.keys():
            prices[key] = int(prices[key])

        # Если задан тикер и он не найден в ценах
        if ticker and not prices.get(ticker):
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"{ticker} Not found")

        # Если тикер задан вернем только его цену
        if ticker:
            return {ticker: int(prices[ticker])}

    return prices


@router.get("/tickers")
async def get_tickers(r: Request):
    """
    Возвращает список тикеров из кеша

    Args:
        r: Запрос

    Returns:
        Список

    """
    async with r.app.state.redis.client() as conn:
        # Получим значение цен из кеша или дефолтное значение
        prices: dict = await conn.hgetall("movement") or PRICES
    return {"tickers": list(prices.keys())}


@router.get("/history/{ticker}")
async def get_history_prices(
        r: Request, ticker: str,
        start: Optional[datetime] = None,
        back: Optional[bool] = False,
        limit: Optional[int] = 10
):
    """
    Возвращает исторические данные из БД

    Args:
        r: Запрос
        ticker: Тикер
        start: Опорная дата от которой выбираются данные
        back: Направление выборки назад
        limit: Лимит значений, выбирающихся за раз

    Returns:
        Котировки

    """
    # Модель с результатом
    quotes: Quotes = Quotes()

    # Если опорная дата не задана, то присвоим текущую
    if not start:
        start = datetime.now().replace(microsecond=0)

    # Если не задан лимит выборки, то вернем все данные после децимации
    if not limit:
        async with r.app.state.db.begin() as conn:
            # Посчитаем количество записей в БД
            query: str = "SELECT count(q.price) FROM public.quotes q WHERE q.ticker = :ticker"
            cursor: Result = await conn.execute(text(query).bindparams(ticker=ticker))
            num_records: int = cursor.scalar_one()

            # Коэффициент децимации
            factor: int = round(num_records/1000)

            query: str = "SELECT q.price FROM public.quotes q WHERE q.ticker = :ticker"
            cursor: Result = await conn.execute(text(query).bindparams(ticker=ticker))
            # Проведем децимацию сигнала
            data: np.ndarray = np.fromiter(cursor.yield_per(1000), dtype=np.dtype((int, 2)))[:, 0]
            quotes.values = [Quote(created="", ticker=ticker, value=value) for value in signal.decimate(data, factor)]

        return quotes

    # Если нужно выбрать данные по лимиту и по направлению
    async with r.app.state.redis.client() as conn:
        # Получим дату последней котировки из кеша
        label: str = await conn.get("label")
        last: datetime = datetime.strptime(label, DATE_FORMAT)

    async with r.app.state.session() as session:
        # Если направление выборки назад
        if back:
            raw: Result = await session.execute(
                select(QuoteScheme).order_by(QuoteScheme.created.desc())
                .where(QuoteScheme.ticker == ticker)
                .where(QuoteScheme.created <= start)
                .limit(limit)
            )
        # Если направление выборки вперед
        else:
            raw: Result = await session.execute(
                select(QuoteScheme).order_by(QuoteScheme.created.asc())
                .where(QuoteScheme.ticker == ticker)
                .where(QuoteScheme.created >= start)
                .limit(limit)
            )

        # Заполним в модели ответа котировки
        for item in raw.scalars():
            quotes.values.append(Quote.from_orm(item))

        # Отсортируем котировки, если было движение назад
        quotes.values.sort(key=lambda x: x.created) if back else None

        # Если дата последней котировки в выборке из БД, то нужно включить обновление графика
        if next(filter(lambda x: x.created.strftime(DATE_FORMAT) == last.strftime(DATE_FORMAT), quotes.values), None):
            quotes.start_live = True

    return quotes
