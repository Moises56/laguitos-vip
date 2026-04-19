#!/usr/bin/env python3
"""Entry point para el servidor web de Laguitos."""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
_backend = _root / "web" / "backend"

if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(_backend)],
    )
