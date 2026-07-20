"""XOR encoding layer."""

from __future__ import annotations

import os
import secrets

from pyveils.core import Encoder, LayerContext
from pyveils.exceptions import EncodingError
from pyveils.plugins import register_encoder


@register_encoder
class XOREncoder(Encoder):
    """XORs payload bytes against a repeating key.

    .. important::
       XOR against a repeating key is trivially breakable by anyone
       with the ciphertext (frequency analysis / known-plaintext).
       This layer provides obfuscation-grade friction only, never
       confidentiality. See the project README's Security &
       Transparency section.

    Options:
        key (bytes | str | None): The XOR key. If omitted, a random
            16-byte key is generated on first use and stored back
            into ``options["key"]`` so the same instance encodes and
            decodes consistently, and so the builder can embed it in
            the runtime snippet.
        key_size (int): Size in bytes of an auto-generated key.
            Defaults to 16. Ignored if ``key`` is provided.
    """

    name = "xor"
    description = "Repeating-key XOR byte obfuscation (not encryption)."

    def _key(self) -> bytes:
        key = self.options.get("key")
        if key is None:
            key_size = int(self.options.get("key_size", 16))
            key = secrets.token_bytes(key_size)
            self.options["key"] = key
        elif isinstance(key, str):
            key = key.encode("utf-8")
            self.options["key"] = key
        if not key:
            raise EncodingError(self.name, "XOR key must not be empty")
        return key

    @staticmethod
    def _xor(data: bytes, key: bytes) -> bytes:
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

    def encode(self, data: bytes, context: LayerContext) -> bytes:
        key = self._key()
        context.record(self.name, key=key)
        return self._xor(data, key)

    def decode(self, data: bytes, context: LayerContext) -> bytes:
        return self._xor(data, self._key())

    def runtime_decode_snippet(self, context: LayerContext) -> str:
        key = self._key()
        return (
            f"(lambda b, k={key!r}: bytes(x ^ k[i % len(k)] for i, x in enumerate(b)))"
        )


__all__ = ["XOREncoder"]
