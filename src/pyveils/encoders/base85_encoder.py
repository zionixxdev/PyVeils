"""Base85 encoding layer."""

from __future__ import annotations

import base64

from pyveils.core import Encoder, LayerContext
from pyveils.exceptions import EncodingError
from pyveils.plugins import register_encoder


@register_encoder
class Base85Encoder(Encoder):
    """Encodes/decodes payload bytes using Base85.

    Options:
        variant (str): Either ``"b85"`` (Python's compact ``base64.b85encode``,
            default) or ``"a85"`` (Adobe-style ``base64.a85encode``).
    """

    name = "base85"
    description = "Base85 reversible byte encoding (b85 or a85 variant)."

    def _variant(self) -> str:
        variant = self.options.get("variant", "b85")
        if variant not in ("b85", "a85"):
            raise EncodingError(self.name, f"unknown variant {variant!r}")
        return variant

    def encode(self, data: bytes, context: LayerContext) -> bytes:
        return base64.a85encode(data) if self._variant() == "a85" else base64.b85encode(data)

    def decode(self, data: bytes, context: LayerContext) -> bytes:
        try:
            return (
                base64.a85decode(data)
                if self._variant() == "a85"
                else base64.b85decode(data)
            )
        except Exception as exc:
            raise EncodingError(self.name, f"failed to decode: {exc}") from exc

    def runtime_decode_snippet(self, context: LayerContext) -> str:
        func = "a85decode" if self._variant() == "a85" else "b85decode"
        return f"(lambda b, __import__=__import__: __import__('base64').{func}(b))"


__all__ = ["Base85Encoder"]
