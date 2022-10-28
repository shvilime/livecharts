import os
import sys
import json
import toml
import pkgutil
import logging
import logging.config
import importlib.util
from dynaconf import Dynaconf
from fastapi import FastAPI, APIRouter
from importlib.machinery import ModuleSpec
from typing import Any, Generator, Optional


settings = Dynaconf(envvar_prefix="scanestas", )


def setup_logger(app: FastAPI, file_path: Optional[str]):
    """
    Настраивает logger и добавляет его в приложение

    Args:
        app: Экземпляр приложения FastAPI
        file_path: Путь к конфигурации logger

    """
    if not file_path:
        logging.warning("Logging configuration does not exists")
        return

    if not os.path.exists(file_path):
        logging.warning(f"{file_path} does not exists. Logging configuration skipped.")
        return

    filename, file_extension = os.path.splitext(file_path)
    parser: dict = {".json": json.load, ".toml": toml.load}

    with open(file_path) as f:
        logging.config.dictConfig(parser.get(file_extension)(f))

    app.state.logger = logging.getLogger(settings.application)


def find_repositories(
        paths: list[str],
        import_name: Optional[str] = "router"
) -> Generator[tuple[str, APIRouter], Any, None]:
    """
    Загружает модули с маршрутами из указанной директории

    Args:
        paths: Путь к модулям
        import_name: Имя переменной, содержащей маршрут, для последующего импорта

    Returns:
        Генератор

    """
    sys.path.extend(paths)
    for module_info in pkgutil.iter_modules(paths):
        logging.info(f'\t-> APIRouter "{module_info.name}" found')
        spec: ModuleSpec = module_info.module_finder.find_spec(module_info.name)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_info.name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            logging.exception(
                f'\t-> APIRouter "{module_info.name}" exception. Skipped. Fix errors to properly load it.'
            )
            continue

        if not hasattr(module, import_name):
            logging.error(f'\t-> APIRouter "{module_info.name}" not loaded, routes not found')
            continue

        yield spec.name, getattr(module, import_name)
        logging.info(f'\t-> APIRouter "{module_info.name}" loaded')


def load_register_routes(app: FastAPI, paths: list[str]):
    """
    Загружает из списка папок модули с маршрутами и регистрирует их в приложении

    Args:
        app: Экземпляр приложения FasAPI
        paths: Список путей

    """
    logging.info("APIRouters loading ...")
    for name, module in find_repositories(paths):
        if not isinstance(module, APIRouter):
            raise TypeError(f"APIRouter {name} have to be instance of {APIRouter}")
        app.include_router(module)

