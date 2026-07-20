"""Exception hierarchy for PyVeils.

All exceptions raised by PyVeils inherit from :class:`PyVeilsError`, so
callers can catch a single base type when they don't need finer-grained
handling.
"""

from __future__ import annotations


class PyVeilsError(Exception):
    """Base class for all exceptions raised by PyVeils."""


class ConfigurationError(PyVeilsError):
    """Raised when a configuration file or object is invalid."""


class LayerError(PyVeilsError):
    """Base class for errors raised by an obfuscation or encoding layer."""

    def __init__(self, layer_name: str, message: str) -> None:
        self.layer_name = layer_name
        super().__init__(f"[{layer_name}] {message}")


class EncodingError(LayerError):
    """Raised when an encoding layer fails to encode or decode data."""


class ObfuscationError(LayerError):
    """Raised when an obfuscation pass fails to transform source code."""


class ParseError(PyVeilsError):
    """Raised when source code cannot be parsed into an AST."""


class BuildError(PyVeilsError):
    """Raised when the final build/output stage fails."""


class PluginError(PyVeilsError):
    """Raised when a plugin fails to load, register, or execute."""


class PluginNotFoundError(PluginError):
    """Raised when a requested plugin/layer name is not registered."""

    def __init__(self, name: str, available: list[str] | None = None) -> None:
        self.name = name
        self.available = available or []
        msg = f"No layer registered under name {name!r}."
        if self.available:
            msg += f" Available layers: {', '.join(sorted(self.available))}"
        super().__init__(msg)


class CLIError(PyVeilsError):
    """Raised for user-facing CLI argument or invocation errors."""


__all__ = [
    "PyVeilsError",
    "ConfigurationError",
    "LayerError",
    "EncodingError",
    "ObfuscationError",
    "ParseError",
    "BuildError",
    "PluginError",
    "PluginNotFoundError",
    "CLIError",
]
