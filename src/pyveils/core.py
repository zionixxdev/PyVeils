"""Core abstractions shared across PyVeils.

This module defines the two fundamental contracts in the framework:

* :class:`Encoder` — a reversible byte/string transform (base64, zlib,
  XOR, marshal, ...). Encoders operate *after* source has been reduced
  to bytes (typically compiled or serialized) and are always paired
  with a matching decode step embedded in the generated loader stub.

* :class:`Obfuscator` — a source-to-source or AST-to-AST transform
  (renaming, dead-code insertion, control-flow flattening, ...).
  Obfuscators are irreversible by design: they change *how* code is
  written without changing *what* it does.

Both share the :class:`Layer` base so the pipeline builder can treat
them uniformly for ordering, naming, and configuration purposes.
"""

from __future__ import annotations

import abc
import ast
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict


@dataclass
class LayerContext:
    """Shared, mutable state threaded through a pipeline run.

    A single ``LayerContext`` instance is created per :func:`Veil.build`
    (or ``encode()``) invocation and passed to every layer in sequence.
    Layers may read prior layers' metadata (e.g. an obfuscator recording
    a rename map that a later reporting step wants to inspect) via
    ``metadata``.

    Attributes:
        source_path: Path to the original input file, for diagnostics.
        options: Global pipeline-level options (e.g. random seed).
        metadata: Free-form bag for layers to record information about
            what they did, keyed by layer name.
    """

    source_path: str
    options: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def record(self, layer_name: str, **info: Any) -> None:
        """Merge ``info`` into ``metadata[layer_name]``."""
        bucket = self.metadata.setdefault(layer_name, {})
        bucket.update(info)


class Layer(abc.ABC):
    """Common base for any pipeline stage (encoder or obfuscator).

    Subclasses must set the ``name`` class variable to a short,
    unique, snake_case identifier. This name is what users reference
    in the fluent API, the ``layers=[...]`` list, config files, and
    the CLI (e.g. ``--rename``, ``--base64``).
    """

    #: Unique registry key, e.g. ``"base64"``, ``"rename"``.
    name: ClassVar[str]

    #: Human-readable one-line description, shown in ``pyveils --help``
    #: and in generated documentation.
    description: ClassVar[str] = ""

    def __init__(self, **options: Any) -> None:
        self.options: Dict[str, Any] = options

    def configure(self, **options: Any) -> "Layer":
        """Return ``self`` after merging in additional options.

        Enables fluent chaining, e.g. ``XOREncoder().configure(key=42)``.
        """
        self.options.update(options)
        return self

    def __repr__(self) -> str:  # pragma: no cover - trivial
        opts = ", ".join(f"{k}={v!r}" for k, v in self.options.items())
        return f"{type(self).__name__}({opts})"


class Encoder(Layer):
    """A reversible transform between ``bytes`` and ``bytes``.

    Every encoder must be able to undo its own transformation via
    :meth:`decode`, since the generated output embeds (or references)
    the decode step in order to reconstruct and execute the original
    program at runtime.
    """

    @abc.abstractmethod
    def encode(self, data: bytes, context: LayerContext) -> bytes:
        """Transform ``data`` forward. Must be paired with :meth:`decode`."""
        raise NotImplementedError

    @abc.abstractmethod
    def decode(self, data: bytes, context: LayerContext) -> bytes:
        """Invert :meth:`encode`. Must satisfy ``decode(encode(x)) == x``."""
        raise NotImplementedError

    @abc.abstractmethod
    def runtime_decode_snippet(self, context: LayerContext) -> str:
        """Return a Python source snippet that decodes this layer at runtime.

        The snippet must define (or extend) a callable chain the
        builder stitches together in the generated loader stub, so
        the protected file can decode itself without importing
        PyVeils at runtime.
        """
        raise NotImplementedError


class Obfuscator(Layer):
    """A source-level or AST-level transformation of Python code.

    Obfuscators receive a parsed module and return a transformed
    module. Working on the AST (rather than raw text) keeps
    transformations composable and syntactically valid by
    construction.
    """

    @abc.abstractmethod
    def transform(self, tree: ast.Module, context: LayerContext) -> ast.Module:
        """Return a new (or mutated) module with this layer's changes applied."""
        raise NotImplementedError


__all__ = ["LayerContext", "Layer", "Encoder", "Obfuscator"]
