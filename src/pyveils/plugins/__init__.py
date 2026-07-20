"""Public plugin API: register your own encoders and obfuscators.

Example — a third-party encoder plugin::

    from pyveils.core import Encoder, LayerContext
    from pyveils.plugins import register_encoder

    @register_encoder
    class Rot13Encoder(Encoder):
        name = "rot13"
        description = "Trivial ROT13 byte rotation (demo only)."

        def encode(self, data: bytes, context: LayerContext) -> bytes:
            return bytes((b + 13) % 256 for b in data)

        def decode(self, data: bytes, context: LayerContext) -> bytes:
            return bytes((b - 13) % 256 for b in data)

        def runtime_decode_snippet(self, context: LayerContext) -> str:
            return "lambda b: bytes((x - 13) % 256 for x in b)"

Once imported (or installed with a matching entry point — see
:mod:`pyveils.plugins.registry`), ``"rot13"`` can be used anywhere a
built-in layer name is accepted: ``Veil(...).rot13()`` via
``__getattr__`` dispatch, ``encode(layers=["rot13"])``, config files,
and the CLI.
"""

from __future__ import annotations

from typing import Type, TypeVar

from pyveils.core import Encoder, Layer, Obfuscator
from pyveils.plugins.registry import discover_entry_point_plugins, encoders, obfuscators

LayerT = TypeVar("LayerT", bound=Layer)


def register_encoder(layer_cls: Type[LayerT], *, override: bool = False) -> Type[LayerT]:
    """Decorator: register an :class:`~pyveils.core.Encoder` subclass."""
    if not issubclass(layer_cls, Encoder):
        raise TypeError(f"{layer_cls.__name__} must subclass pyveils.core.Encoder")
    return encoders.register(layer_cls, override=override)


def register_obfuscator(layer_cls: Type[LayerT], *, override: bool = False) -> Type[LayerT]:
    """Decorator: register an :class:`~pyveils.core.Obfuscator` subclass."""
    if not issubclass(layer_cls, Obfuscator):
        raise TypeError(f"{layer_cls.__name__} must subclass pyveils.core.Obfuscator")
    return obfuscators.register(layer_cls, override=override)


__all__ = [
    "register_encoder",
    "register_obfuscator",
    "encoders",
    "obfuscators",
    "discover_entry_point_plugins",
]
