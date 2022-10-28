from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException, RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from application.core.events import create_start_app_handler, create_stop_app_handler
from application.core.errors import (
    http_error_handler,
    http422_error_handler,
    unexpected_error_handler
)

from application.core import routes
from application.core.scheduler import run_scheduler
from application.core.config import settings, setup_logger, load_register_routes


def prepare_application() -> FastAPI:
    # Создадим экземпляр приложения
    application: FastAPI = FastAPI()

    # Зарегистрируем функции, запускающуюся при старте и остановке
    application.add_event_handler("startup", create_start_app_handler(application))
    application.add_event_handler("shutdown", create_stop_app_handler(application))

    # Зарегистрируем средний слой, для CORS
    application.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    # Зарегистрируем обработчики ошибок
    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(StarletteHTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)
    application.add_exception_handler(Exception, unexpected_error_handler)

    # Настроим глобальный logger приложения
    setup_logger(application, settings.logging)

    # Зарегистрируем маршруты
    application.include_router(routes.router)
    load_register_routes(application, settings.route_path)

    # Запустим планировщик
    application.scheduler = run_scheduler()

    return application


# Настроим основное приложение
app: FastAPI = prepare_application()
