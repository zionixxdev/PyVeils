# PyVeils

**A modern, extensible, plugin-based Python code obfuscation framework.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy-lang.org/)

PyVeils applies configurable, composable layers of obfuscation and encoding to
Python source files while preserving their original behavior. It's built
around a small set of clean interfaces — `Encoder` and `Obfuscator` — so
built-in layers and third-party plugins are registered and used identically.

```python
from pyveils import Veil

(
    Veil("main.py")
        .rename()
        .encrypt_strings()
        .marshal()
        .zlib()
        .base64()
        .dead_code()
        .build("protected.py")
)
```

---

## Table of Contents

- [Why PyVeils](#why-pyveils)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Command Line Interface](#command-line-interface)
- [Available Layers](#available-layers)
- [Configuration Files](#configuration-files)
- [Plugin System](#plugin-system)
- [Architecture](#architecture)
- [Security & Transparency](#security--transparency)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## Why PyVeils

- **Fluent, chainable API** — build a pipeline in one expression, or assemble
  it programmatically from a list of layer names.
- **Plugin-first architecture** — every built-in layer is registered through
  the exact same mechanism available to third-party packages. There is no
  special internal fast path.
- **Composable by design** — encoders and obfuscators are isolated,
  independently testable units that can be freely chained and reordered.
- **Multiple configuration surfaces** — Python API, JSON/TOML/YAML config
  files, or CLI flags, all validated against the same schema.
- **Honest about what it does** — PyVeils obfuscates; it does not encrypt.
  See [Security & Transparency](#security--transparency).

## Installation

```bash
pip install pyveils
```

For plugin development or contributing, install the development extras:

```bash
pip install "pyveils[dev]"
```

## Quickstart

### Fluent API

```python
from pyveils import Veil

Veil("main.py").rename().marshal().zlib().base64().build("protected.py")
```

### Functional API

```python
from pyveils import encode

encode(
    input="main.py",
    output="protected.py",
    layers=["rename", "marshal", "zlib", "base64"],
)
```

Both APIs go through the same underlying pipeline builder — pick whichever
reads better for your use case.

## Command Line Interface

```bash
# Apply every default layer
pyveils main.py --all

# Choose the output path
pyveils main.py -o protected.py

# Use a numeric obfuscation level (higher = more aggressive)
pyveils main.py --level 5

# Hand-pick specific layers, in order
pyveils main.py --rename --marshal --zlib --base64

# Utility flags
pyveils --version
pyveils --help
```

## Available Layers

**Encoders** (reversible, applied to the compiled/serialized payload):

| Layer     | Name       | Notes                                      |
|-----------|------------|---------------------------------------------|
| Base64    | `base64`   | Optional URL-safe alphabet                   |
| Base32    | `base32`   | RFC 4648                                     |
| Base85    | `base85`   | `b85` or `a85` variant                       |
| Hex       | `hex`      | Plain hexadecimal text                       |
| marshal   | `marshal`  | CPython-version-specific                     |
| zlib      | `zlib`     | Configurable compression level               |
| gzip      | `gzip`     | Configurable compression level               |
| lzma      | `lzma`     | Highest compression ratio                    |
| XOR       | `xor`      | Repeating-key byte XOR                       |

**Obfuscators** (source/AST-level transforms):

`rename` (variables/functions/classes) · `import_alias` · `encrypt_strings` ·
`ast_rewrite` · `dead_code` · `dummy_functions` · `dummy_classes` ·
`strip_comments` · `strip_docstrings` · `control_flow` · `pyc_compile`

Every layer exposes its own configurable parameters — see the
[API Reference](docs/) for details.

## Configuration Files

PyVeils accepts the same pipeline definition as JSON, TOML, or YAML:

```toml
# pyveils.toml
input = "main.py"
output = "protected.py"
layers = ["rename", "encrypt_strings", "marshal", "zlib", "base64"]

[layers.xor]
key_size = 32

[layers.zlib]
level = 9
```

```bash
pyveils --config pyveils.toml
```

## Plugin System

Add new encoders or obfuscators without touching PyVeils' core:

```python
from pyveils.core import Encoder, LayerContext
from pyveils.plugins import register_encoder

@register_encoder
class Rot13Encoder(Encoder):
    name = "rot13"
    description = "Trivial ROT13 byte rotation (demo only)."

    def encode(self, data: bytes, context: LayerContext) -> bytes:
        return bytes((b + 13) % 256 for b in data)

    def decode(self, data: bytes, context: LayerContext) -> bytes:
        return bytes((b - 13) % 256 for b in data)

    def runtime_decode_snippet(self, context: LayerContext) -> str:
        return "lambda b: bytes((x - 13) % 256 for x in b)"
```

Once imported, `"rot13"` works anywhere a built-in layer name does — the
fluent API, `layers=[...]`, config files, and the CLI. Packages can also
register automatically via a `pyveils.plugins` entry point; see
[docs/plugin-development.md](docs/plugin-development.md).

## Architecture

```
src/pyveils/
├── core.py         # Layer / Encoder / Obfuscator / LayerContext base contracts
├── encoders/        # Reversible byte-level transforms (one file per encoder)
├── obfuscators/      # Source/AST-level transforms (one file per pass)
├── ast_tools/        # Shared AST parsing/rewriting utilities
├── compiler/          # Source -> code object / bytecode compilation stage
├── builder/            # Pipeline orchestration and output generation
├── plugins/             # Registry, discovery, and the register_* decorators
├── cli/                  # Typer-based command line interface
├── config/                # JSON/TOML/YAML config loading & validation
├── logging/                # Opt-in library logger
├── exceptions/              # Exception hierarchy
└── utils/                    # Shared, dependency-free helpers
```

Each module has a single responsibility, and every encoder/obfuscator is
independently unit-tested. See [tests/](tests/) for the full suite.

## Security & Transparency

**PyVeils is a code obfuscation framework, not a cryptographic security
solution.** Reversible techniques such as Base64, `marshal`, compression, or
XOR provide obfuscation only — they raise the effort required to read or
modify the code, but do not provide confidentiality or tamper-resistance
guarantees. Do not rely on PyVeils to protect secrets (API keys, credentials)
embedded in source; use a proper secrets-management solution for those.

## Development

```bash
git clone https://github.com/ZionixxDev/PyVeils.git
cd PyVeils
pip install -e ".[dev]"

pytest                 # run the test suite
black src tests        # format
ruff check src tests   # lint
mypy src               # type-check
```

## Contributing

Contributions are welcome — please read [CONTRIBUTING.md](CONTRIBUTING.md)
and our [Code of Conduct](CODE_OF_CONDUCT.md) before opening a PR. See
[SECURITY.md](SECURITY.md) to report a vulnerability.

## License

PyVeils is released under the [MIT License](LICENSE).
