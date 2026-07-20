"""Base64 encoding layer."""

from __future__ import annotations

import base64

from pyveils.core import Encoder, LayerContext
from pyveils.exceptions import EncodingError
from pyveils.plugins import register_encoder


@register_encoder
class Base64Encoder(Encoder):
    """Encodes/decodes payload bytes using standard Base64 (RFC 4648).

    Options:
        urlsafe (bool): Use the URL-safe alphabet (``-`` / ``_`` instead
            of ``+`` / ``/``). Defaults to ``False``.
    """

    name = "base64"
    description = "Standard Base64 (RFC 4648) reversible byte encoding."

    def encode(self, data: bytes, context: LayerContext) -> bytes:
        urlsafe = self.options.get("urlsafe", False)
        return base64.urlsafe_b64encode(data) if urlsafe else base64.b64encode(data)

    def decode(self, data: bytes, context: LayerContext) -> bytes:
        urlsafe = self.options.get("urlsafe", False)
        try:
            return (
                base64.urlsafe_b64decode(data) if urlsafe else base64.b64decode(data)
            )
        except Exception as exc:
            raise EncodingError(self.name, f"failed to decode: {exc}") from exc

    def runtime_decode_snippet(self, context: LayerContext) -> str:
        module = "base64"
        func = "urlsafe_b64decode" if self.options.get("urlsafe", False) else "b64decode"
        return f"(lambda b, __import__=__import__: __import__({module!r}).{func}(b))"


__all__ = ["Base64Encoder"]
