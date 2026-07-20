"""Plugin registration and discovery for PyVeils layers.

PyVeils' built-in encoders and obfuscators are registered exactly like
third-party plugins: through the same :func:`register` decorator and
the same :class:`Registry`. This keeps the "core" and "plugin" code
paths identical, which is the whole point of a plugin architecture —
there is no special-cased internal fast path a third party can't use.

Third-party packages can also register layers automatically via
Python entry points, under the ``"pyveils.plugins"`` group. For
example, in a plugin package's ``pyproject.toml``::

    [project.entry-points."pyveils.plugins"]
    rot13 = "pyveils_rot13:Rot13Encoder"

Once installed, :func:`discover_entry_point_plugins` (called once,
lazily, on first pipeline build) will import and register it.
"""

from __future__ import annotations

import importlib.metadata as importlib_metadata
from typing import Dict, Iterator, Type, TypeVar

from pyveils.core import Layer
from pyveils.exceptions import PluginError, PluginNotFoundError
from pyveils.logging import get_logger

_log = get_logger("plugins.registry")

_ENTRY_POINT_GROUP = "pyveils.plugins"

LayerT = TypeVar("LayerT", bound=Layer)


class Registry:
    """A name -> Layer-class registry with duplicate protection.

    Two independent registries are maintained at module scope in
    :mod:`pyveils.plugins`: one for encoders, one for obfuscators.
    Keeping them separate lets the CLI and config validators reject,
    e.g., using an obfuscator name where an encoder is expected.
    """

    def __init__(self, kind: str) -> None:
        self._kind = kind
        self._layers: Dict[str, Type[Layer]] = {}

    def register(self, layer_cls: Type[LayerT], *, override: bool = False) -> Type[LayerT]:
        """Register ``layer_cls`` under its ``name`` attribute.

        Args:
            layer_cls: A concrete :class:`~pyveils.core.Layer` subclass
                with a non-empty ``name`` class attribute.
            override: If ``False`` (default), raises if the name is
                already registered — this catches accidental
                name collisions between plugins early.

        Returns:
            ``layer_cls`` unchanged, so this can be used as a decorator.
        """
        name = getattr(layer_cls, "name", None)
        if not name:
            raise PluginError(
                f"{layer_cls.__name__} must define a non-empty 'name' class "
                f"attribute to be registered as a {self._kind}."
            )
        if name in self._layers and not override:
            existing = self._layers[name]
            if existing is not layer_cls:
                raise PluginError(
                    f"A {self._kind} named {name!r} is already registered "
                    f"({existing.__module__}.{existing.__qualname__}). "
                    f"Pass override=True to replace it intentionally."
                )
        self._layers[name] = layer_cls
        _log.debug("Registered %s %r -> %s", self._kind, name, layer_cls)
        return layer_cls

    def get(self, name: str) -> Type[Layer]:
        """Look up a registered layer class by name.

        Raises:
            PluginNotFoundError: if ``name`` isn't registered.
        """
        try:
            return self._layers[name]
        except KeyError:
            raise PluginNotFoundError(name, available=list(self._layers)) from None

    def create(self, name: str, **options: object) -> Layer:
        """Instantiate the layer registered under ``name`` with ``options``."""
        return self.get(name)(**options)

    def names(self) -> Iterator[str]:
        """Iterate over all registered layer names."""
        return iter(sorted(self._layers))

    def __contains__(self, name: str) -> bool:
        return name in self._layers

    def __len__(self) -> int:
        return len(self._layers)


encoders = Registry("encoder")
obfuscators = Registry("obfuscator")

_entry_points_loaded = False


def discover_entry_point_plugins(*, force: bool = False) -> None:
    """Import and register third-party plugins declared via entry points.

    This is idempotent and cheap after the first call. It is invoked
    automatically the first time a pipeline is built (see
    :mod:`pyveils.builder.pipeline`), so most users never need to call
    it directly.

    Args:
        force: Re-scan entry points even if already loaded once.
    """
    global _entry_points_loaded
    if _entry_points_loaded and not force:
        return

    try:
        eps = importlib_metadata.entry_points(group=_ENTRY_POINT_GROUP)
    except Exception as exc:  # pragma: no cover - defensive
        _log.warning("Failed to query entry points: %s", exc)
        _entry_points_loaded = True
        return

    for ep in eps:
        try:
            layer_cls = ep.load()
        except Exception as exc:
            raise PluginError(
                f"Failed to load plugin entry point {ep.name!r} "
                f"({ep.value}): {exc}"
            ) from exc

        if not (isinstance(layer_cls, type) and issubclass(layer_cls, Layer)):
            raise PluginError(
                f"Entry point {ep.name!r} ({ep.value}) does not resolve to a "
                f"Layer subclass."
            )

        from pyveils.core import Encoder, Obfuscator

        if issubclass(layer_cls, Encoder):
            encoders.register(layer_cls)
        elif issubclass(layer_cls, Obfuscator):
            obfuscators.register(layer_cls)
        else:  # pragma: no cover - defensive, Layer has no other direct subclass
            raise PluginError(
                f"Entry point {ep.name!r} must subclass Encoder or Obfuscator."
            )

    _entry_points_loaded = True


__all__ = [
    "Registry",
    "encoders",
    "obfuscators",
    "discover_entry_point_plugins",
]
