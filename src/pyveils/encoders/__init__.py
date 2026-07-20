"""Built-in encoding layers.

Each encoder lives in its own module (single responsibility) and is
registered into the global :data:`pyveils.plugins.encoders` registry
by importing it here. Importing :mod:`pyveils.encoders` is therefore
sufficient to make every built-in encoder available by name.
"""

from __future__ import annotations

from pyveils.encoders.base32_encoder import Base32Encoder
from pyveils.encoders.base64_encoder import Base64Encoder
from pyveils.encoders.base85_encoder import Base85Encoder
from pyveils.encoders.gzip_encoder import GzipEncoder
from pyveils.encoders.hex_encoder import HexEncoder
from pyveils.encoders.lzma_encoder import LzmaEncoder
from pyveils.encoders.marshal_encoder import MarshalEncoder
from pyveils.encoders.xor_encoder import XOREncoder
from pyveils.encoders.zlib_encoder import ZlibEncoder

__all__ = [
    "Base32Encoder",
    "Base64Encoder",
    "Base85Encoder",
    "GzipEncoder",
    "HexEncoder",
    "LzmaEncoder",
    "MarshalEncoder",
    "XOREncoder",
    "ZlibEncoder",
]
