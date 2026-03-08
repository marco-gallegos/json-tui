"""Logging configuration for performance metrics."""

from __future__ import annotations

import sys
import time
from functools import wraps
from pathlib import Path
from typing import Callable, TypeVar

from loguru import logger

T = TypeVar("T")


def setup(dev_mode: bool, log_file: Path | None = None) -> None:
    """Configure logging based on dev mode."""
    logger.remove()
    if dev_mode:
        if log_file:
            logger.add(
                log_file,
                level="DEBUG",
                format="{time:HH:mm:ss} | {message}",
            )
        else:
            logger.add(
                sys.stderr,
                format="<level>{time:HH:mm:ss}</level> | <level>{message}</level>",
                level="DEBUG",
            )
    else:
        logger.disable("json_tui")


def timeit(name: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to measure and log execution time in milliseconds."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: ..., **kwargs: ...) -> T:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            logger.debug(f"{name}: {elapsed:.2f}ms")
            return result

        return wrapper

    return decorator
