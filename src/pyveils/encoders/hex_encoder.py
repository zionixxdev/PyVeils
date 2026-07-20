"""Hexadecimal encoding layer."""

from __future__ import annotations

from pyveils.core import Encoder, LayerContext
from pyveils.exceptions import EncodingError
from pyveils.plugins import register_encoder


@register_encoder
class HexEncoder(Encoder):
    """Encodes/decodes payload bytes as hexadecimal text."""

    name = "hex"
    description = "Hexadecimal reversible byte encoding."

    def encode(self, data: bytes, context: LayerContext) -> bytes:
        return data.hex().encode("ascii")

    def decode(self, data: bytes, context: LayerContext) -> bytes:
        try:
            return bytes.fromhex(data.decode("ascii"))
        except Exception as exc:
            raise EncodingError(self.name, f"failed to decode: {exc}") from exc

    def runtime_decode_snippet(self, context: LayerContext) -> str:
        return "(lambda b: bytes.fromhex(b.decode('ascii')))"


__all__ = ["HexEncoder"]
