"""Base32 encoding layer."""

from __future__ import annotations

import base64

from pyveils.core import Encoder, LayerContext
from pyveils.exceptions import EncodingError
from pyveils.plugins import register_encoder


@register_encoder
class Base32Encoder(Encoder):
    """Encodes/decodes payload bytes using standard Base32 (RFC 4648)."""

    name = "base32"
    description = "Standard Base32 (RFC 4648) reversible byte encoding."

    def encode(self, data: bytes, context: LayerContext) -> bytes:
        return base64.b32encode(data)

    def decode(self, data: bytes, context: LayerContext) -> bytes:
        try:
            return base64.b32decode(data)
        except Exception as exc:
            raise EncodingError(self.name, f"failed to decode: {exc}") from exc

    def runtime_decode_snippet(self, context: LayerContext) -> str:
        return "(lambda b, __import__=__import__: __import__('base64').b32decode(b))"


__all__ = ["Base32Encoder"]
