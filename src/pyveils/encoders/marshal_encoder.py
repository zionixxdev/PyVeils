"""marshal serialization layer.

.. warning::
   ``marshal``'s format is version-specific to the CPython release
   that wrote it. Output produced by this encoder should be decoded
   by the same (or a compatible) Python minor version it was built
   under. This is documented prominently in the generated output's
   header comment by the builder.
"""

from __future__ import annotations

import marshal

from pyveils.core import Encoder, LayerContext
from pyveils.exceptions import EncodingError
from pyveils.plugins import register_encoder


@register_encoder
class MarshalEncoder(Encoder):
    """Serializes/deserializes the payload via the ``marshal`` module.

    Operates on the payload as an opaque ``bytes`` object: encoding
    wraps it with ``marshal.dumps``, decoding unwraps it with
    ``marshal.loads``. This is typically layered right after the
    compiler stage, where the payload may instead be a code object
    (see :mod:`pyveils.compiler`), in which case marshal is doing its
    "native" job of serializing bytecode.
    """

    name = "marshal"
    description = "marshal serialization (CPython-version-specific)."

    def encode(self, data: bytes, context: LayerContext) -> bytes:
        return marshal.dumps(data)

    def decode(self, data: bytes, context: LayerContext) -> bytes:
        try:
            result = marshal.loads(data)
        except Exception as exc:
            raise EncodingError(self.name, f"failed to unmarshal: {exc}") from exc
        if not isinstance(result, bytes):
            raise EncodingError(
                self.name,
                f"expected unmarshalled payload to be bytes, got {type(result).__name__}",
            )
        return result

    def runtime_decode_snippet(self, context: LayerContext) -> str:
        return "(lambda b, __import__=__import__: __import__('marshal').loads(b))"


__all__ = ["MarshalEncoder"]
