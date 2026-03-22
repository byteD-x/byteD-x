#!/usr/bin/env python3
"""Generate a classic GitHub contribution snake SVG.

Inputs:
- `--github-user`: GitHub login to query.
- `--theme`: `light` or `dark`.
- `--output`: target SVG path.

Output:
- Writes a self-contained animated SVG file.

Failure:
- Exits non-zero when the GitHub token is missing, the GraphQL request fails,
  or the SVG cannot be written.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_IMPL_PATH = Path(__file__).with_name("_snake_impl.py")
_SPEC = importlib.util.spec_from_file_location("byteD_x_snake_impl", _IMPL_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Unable to load snake implementation from {_IMPL_PATH}.")
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)

for _name in dir(_MODULE):
    if _name.startswith("__") and _name not in {"__doc__", "__all__"}:
        continue
    globals()[_name] = getattr(_MODULE, _name)


if __name__ == "__main__":
    raise SystemExit(main())
