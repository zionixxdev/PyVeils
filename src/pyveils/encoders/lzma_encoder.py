"""LZMA compression layer."""

from __future__ import annotations

import lzma

from pyveils.core import Encoder, LayerContext
from pyveils.exceptions import EncodingError
from pyveils.plugins import register_encoder


@register_encoder
class LzmaEncoder(Encoder):
    """Compresses/decompresses payload bytes with LZMA (``.xz`` container).

    Generally yields the smallest output of the compression encoders,
    at the cost of higher CPU time.
    """

    name = "lzma"
    description = "LZMA compression (xz container), highest compression ratio."

    def encode(self, data: bytes, context: LayerContext) -> bytes:
        return lzma.compress(data)

    def decode(self, data: bytes, context: LayerContext) -> bytes:
        try:
            return lzma.decompress(data)
        except Exception as exc:
            raise EncodingError(self.name, f"failed to decompress: {exc}") from exc

    def runtime_decode_snippet(self, context: LayerContext) -> str:
        return "(lambda b, __import__=__import__: __import__('lzma').decompress(b))"


__all__ = ["LzmaEncoder"]
