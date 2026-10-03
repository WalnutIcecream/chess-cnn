#!/usr/bin/env python3
"""Check that the moveexp environment is complete: dependencies plus a working Stockfish.

Run inside the venv (or the dev shell)::

    python scripts/check_env.py                       # $STOCKFISH_PATH or 'stockfish' on PATH
    python scripts/check_env.py --engine ~/tools/stockfish

Prints PASS/FAIL for each check and exits non-zero if anything failed.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

#: module name -> human label. The data stack is what Parquet (M5-M7) needs; chess/pydantic
#: are the analysis core.
MODULES = {
    "numpy": "numpy",
    "pandas": "pandas",
    "pyarrow": "pyarrow",
    "zstandard": "zstandard",
    "chess": "python-chess",
    "pydantic": "pydantic",
}


def check_imports() -> bool:
    ok = True
    for module, label in MODULES.items():
        try:
            mod = __import__(module)
        except Exception as exc:  # noqa: BLE001 - report every failure, do not abort
            ok = False
            print(f"FAIL  import {label}: {exc}")
            continue
        version = getattr(mod, "__version__", "?")
        print(f"PASS  import {label} ({version})")
    return ok


def find_stockfish(explicit: str | None = None) -> str | None:
    """Stockfish lookup order: --engine flag, then STOCKFISH_PATH, then PATH."""
    if explicit:
        return explicit
    env = os.environ.get("STOCKFISH_PATH")
    if env and (os.path.isfile(env) or shutil.which(env)):
        return env
    return shutil.which("stockfish")


def check_stockfish(path: str | None) -> bool:
    if not path:
        print("FAIL  stockfish: not found (set STOCKFISH_PATH or put 'stockfish' on PATH)")
        return False
    try:
        proc = subprocess.run(
            [path, "uci"],
            input="uci\nquit\n",
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL  stockfish ({path}): {exc}")
        return False
    name = author = None
    for line in proc.stdout.splitlines():
        if line.startswith("id name "):
            name = line[len("id name ") :]
        elif line.startswith("id author "):
            author = line[len("id author ") :]
    if name:
        suffix = f" (author: {author})" if author else ""
        print(f"PASS  stockfish ({path}): {name}{suffix}")
        return True
    print(f"FAIL  stockfish ({path}): did not report an 'id name' in its UCI handshake")
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--engine", help="Stockfish binary (default: $STOCKFISH_PATH or 'stockfish' on PATH)."
    )
    args = parser.parse_args(argv)

    print(f"Python: {sys.version.split()[0]}  ({sys.executable})")
    imports_ok = check_imports()
    engine_ok = check_stockfish(find_stockfish(args.engine))

    print()
    if imports_ok and engine_ok:
        print("ALL CHECKS PASSED")
        return 0
    print("SOME CHECKS FAILED — see docs/SETUP.md")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
