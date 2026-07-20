"""zlib compression layer."""

from __future__ import annotations

import zlib

from pyveils.core import Encoder, LayerContext
from pyveils.exceptions import EncodingError
from pyveils.plugins import register_encoder


@register_encoder
class ZlibEncoder(Encoder):
    """Compresses/decompresses payload bytes with zlib (DEFLATE + header).

    Options:
        level (int): Compression level 0-9 (default 9, best compression).
    """

    name = "zlib"
    description = "zlib (DEFLATE) compression, also reduces output size."

    def encode(self, data: bytes, context: LayerContext) -> bytes:
        level = int(self.options.get("level", 9))
        return zlib.compress(data, level)

    def decode(self, data: bytes, context: LayerContext) -> bytes:
        try:
            return zlib.decompress(data)
        except Exception as exc:
            raise EncodingError(self.name, f"failed to decompress: {exc}") from exc

    def runtime_decode_snippet(self, context: LayerContext) -> str:
        return "(lambda b, __import__=__import__: __import__('zlib').decompress(b))"


__all__ = ["ZlibEncoder"]
