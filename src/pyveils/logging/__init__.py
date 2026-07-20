"""Centralized logging configuration for PyVeils.

PyVeils follows the standard library-logging convention: it never
configures handlers on the root logger itself, and instead exposes a
named logger (``"pyveils"``) plus a convenience :func:`configure`
function that host applications (or the CLI) can call to attach a
handler with sensible formatting.
"""

from __future__ import annotations

import logging
import sys
from typing import Optional

_LOGGER_NAME = "pyveils"

logger = logging.getLogger(_LOGGER_NAME)
logger.addHandler(logging.NullHandler())

_DEFAULT_FORMAT = "[%(levelname)s] %(name)s: %(message)s"


def configure(
    level: int = logging.INFO,
    *,
    fmt: str = _DEFAULT_FORMAT,
    stream: Optional[object] = None,
) -> logging.Logger:
    """Attach a stream handler to the PyVeils logger and set its level.

    This is opt-in: library code never calls this automatically. The
    CLI calls it on startup, and host applications embedding PyVeils
    as a library may call it if they want PyVeils' own log output.

    Args:
        level: Logging level, e.g. ``logging.DEBUG``.
        fmt: A ``logging.Formatter``-compatible format string.
        stream: Output stream for the handler. Defaults to ``sys.stderr``.

    Returns:
        The configured ``"pyveils"`` logger.
    """
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(logging.Formatter(fmt))

    # Avoid stacking duplicate handlers if configure() is called twice.
    logger.handlers = [
        h for h in logger.handlers if not isinstance(h, logging.NullHandler)
    ]
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a child logger under the ``"pyveils"`` namespace.

    Args:
        name: Optional dotted suffix, e.g. ``"encoders.base64"`` yields
            a logger named ``"pyveils.encoders.base64"``.
    """
    return logger.getChild(name) if name else logger


__all__ = ["logger", "configure", "get_logger"]
