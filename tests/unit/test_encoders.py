from __future__ import annotations

import pytest

from pyveils import encoders as _encoders_module  # noqa: F401  (ensures registration)
from pyveils.encoders.base32_encoder import Base32Encoder
from pyveils.encoders.base64_encoder import Base64Encoder
from pyveils.encoders.base85_encoder import Base85Encoder
from pyveils.encoders.gzip_encoder import GzipEncoder
from pyveils.encoders.hex_encoder import HexEncoder
from pyveils.encoders.lzma_encoder import LzmaEncoder
from pyveils.encoders.marshal_encoder import MarshalEncoder
from pyveils.encoders.xor_encoder import XOREncoder
from pyveils.encoders.zlib_encoder import ZlibEncoder
from pyveils.exceptions import EncodingError
from pyveils.plugins import encoders as registry

ALL_ENCODER_CLASSES = [
    Base32Encoder,
    Base64Encoder,
    Base85Encoder,
    GzipEncoder,
    HexEncoder,
    LzmaEncoder,
    MarshalEncoder,
    XOREncoder,
    ZlibEncoder,
]

SAMPLE_PAYLOADS = [
    b"",
    b"hello world",
    b"\x00\x01\x02\xff\xfe" * 10,
    ("print('hello, world!')\n" * 50).encode("utf-8"),
]


@pytest.mark.parametrize("encoder_cls", ALL_ENCODER_CLASSES)
@pytest.mark.parametrize("payload", SAMPLE_PAYLOADS)
def test_round_trip(encoder_cls, payload, context):
    encoder = encoder_cls()
    encoded = encoder.encode(payload, context)
    assert isinstance(encoded, bytes)
    decoded = encoder.decode(encoded, context)
    assert decoded == payload


@pytest.mark.parametrize("encoder_cls", ALL_ENCODER_CLASSES)
def test_runtime_decode_snippet_is_valid_python_expression(encoder_cls, context):
    encoder = encoder_cls()
    # Ensure the key/option is materialized before rendering the snippet
    # (relevant for XOR, whose key is generated lazily).
    encoder.encode(b"seed", context)
    snippet = encoder.runtime_decode_snippet(context)
    compiled = compile(snippet, "<runtime_decode_snippet>", "eval")
    fn = eval(compiled)
    assert callable(fn)


@pytest.mark.parametrize("encoder_cls", ALL_ENCODER_CLASSES)
def test_registered_under_its_own_name(encoder_cls):
    assert encoder_cls.name in registry
    assert registry.get(encoder_cls.name) is encoder_cls


def test_base64_urlsafe_option(context):
    encoder = Base64Encoder(urlsafe=True)
    payload = bytes(range(256))
    encoded = encoder.encode(payload, context)
    assert b"+" not in encoded and b"/" not in encoded
    assert encoder.decode(encoded, context) == payload


def test_base85_variant_option(context):
    payload = b"variant test payload"
    b85 = Base85Encoder(variant="b85")
    a85 = Base85Encoder(variant="a85")
    assert b85.encode(payload, context) != a85.encode(payload, context)
    assert b85.decode(b85.encode(payload, context), context) == payload
    assert a85.decode(a85.encode(payload, context), context) == payload


def test_base85_rejects_unknown_variant(context):
    encoder = Base85Encoder(variant="nonsense")
    with pytest.raises(EncodingError):
        encoder.encode(b"data", context)


def test_xor_generates_and_reuses_key(context):
    encoder = XOREncoder()
    assert "key" not in encoder.options
    encoded = encoder.encode(b"payload", context)
    assert "key" in encoder.options
    key_after_encode = encoder.options["key"]
    # Decoding with the same instance must reuse the same generated key.
    assert encoder.decode(encoded, context) == b"payload"
    assert encoder.options["key"] == key_after_encode


def test_xor_explicit_string_key_is_encoded_to_bytes(context):
    encoder = XOREncoder(key="mykey")
    encoded = encoder.encode(b"payload data", context)
    assert encoder.decode(encoded, context) == b"payload data"
    assert encoder.options["key"] == b"mykey"


def test_xor_rejects_empty_key(context):
    encoder = XOREncoder(key="")
    with pytest.raises(EncodingError):
        encoder.encode(b"data", context)


def test_hex_decode_error_wraps_exception(context):
    encoder = HexEncoder()
    with pytest.raises(EncodingError):
        encoder.decode(b"not-valid-hex!!", context)


def test_marshal_rejects_non_bytes_payload(context):
    import marshal as _marshal

    encoder = MarshalEncoder()
    non_bytes_marshalled = _marshal.dumps({"not": "bytes"})
    with pytest.raises(EncodingError):
        encoder.decode(non_bytes_marshalled, context)


def test_zlib_compression_level_option(context):
    payload = b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    fast = ZlibEncoder(level=1).encode(payload, context)
    best = ZlibEncoder(level=9).encode(payload, context)
    assert ZlibEncoder().decode(fast, context) == payload
    assert ZlibEncoder().decode(best, context) == payload
