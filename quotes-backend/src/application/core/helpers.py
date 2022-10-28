import logging
import importlib
from typing import Any, Iterable, Mapping, Optional


def __import_module(package: str, cls: str) -> Optional[Any]:
    try:
        return getattr(importlib.import_module(package), cls)
    except ImportError:
        logging.error(f"No module named '{package}'. Please install.")
        return None


def load_module(package: str, cls: str, args: Optional[Iterable] = None, kwargs: Optional[Mapping] = None) -> Any:
    klass = __import_module(package, cls)
    return klass(*args or (), **kwargs or {}) if klass else None
