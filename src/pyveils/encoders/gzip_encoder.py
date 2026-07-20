"""gzip compression layer."""

from __future__ import annotations

import gzip

from pyveils.core import Encoder, LayerContext
from pyveils.exceptions import EncodingError
from pyveils.plugins import register_encoder


@register_encoder
class GzipEncoder(Encoder):
    """Compresses/decompresses payload bytes with gzip.

    Options:
        compresslevel (int): Compression level 0-9 (default 9).
    """

    name = "gzip"
    description = "gzip compression (DEFLATE + gzip container/header)."

    def encode(self, data: bytes, context: LayerContext) -> bytes:
        level = int(self.options.get("compresslevel", 9))
        return gzip.compress(data, compresslevel=level)

    def decode(self, data: bytes, context: LayerContext) -> bytes:
        try:
            return gzip.decompress(data)
        except Exception as exc:
            raise EncodingError(self.name, f"failed to decompress: {exc}") from exc

    def runtime_decode_snippet(self, context: LayerContext) -> str:
        return "(lambda b, __import__=__import__: __import__('gzip').decompress(b))"


__all__ = ["GzipEncoder"]
