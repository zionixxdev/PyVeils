from __future__ import annotations

import pytest

from pyveils.core import LayerContext


@pytest.fixture
def context() -> LayerContext:
    """A fresh LayerContext for a fake 'main.py' source file."""
    return LayerContext(source_path="main.py")
