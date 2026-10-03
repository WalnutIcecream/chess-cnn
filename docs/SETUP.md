# Setup

This project has **no machine-specific paths**. The engine binary and the data directory are
resolved at runtime from a lookup order, and nothing important may live under `/tmp`.

---

## 1. Python environment (in-repo venv)

Python 3.11+ is required. Create the venv **inside the repo** (it is git-ignored):

```bash
cd /path/to/chess-ai
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'          # analysis core + pytest + ruff
pip install -e '.[torch]'        # optional, only needed for Stage 4 (the neural model)
```

The Parquet tooling (Milestones 5–7) needs `numpy`, `pandas`, `pyarrow`; these are core
dependencies and come with `.[dev]`, but on **NixOS** they need the C++ standard library —
see §3.

---

## 2. Stockfish

Stockfish is GPL-3.0 and is **not vendored**. Provide it yourself and point the project at it.

### 2.1 Install into a persistent location

From a package manager (easiest):

```bash
# NixOS
nix-env -iA nixpkgs.stockfish          # or add to configuration.nix

# Debian/Ubuntu
sudo apt install stockfish

# macOS (Homebrew)
brew install stockfish
```

Or build from source into `~/tools/`:

```bash
mkdir -p ~/tools
git clone https://github.com/official-stockfish/Stockfish.git ~/tools/Stockfish
cd ~/tools/Stockfish/src
make -j "$(nproc)" profile-build ARCH=x86-64-avx2     # pick ARCH for your CPU; see Makefile
cp stockfish ~/tools/stockfish
```

> Note: the nixpkgs Stockfish 18 build has been observed to return garbage on some positions
> and crash on illegal input. Prefer Stockfish 16+ from source or a distro package.

### 2.2 Point the project at it

The engine path resolves in this order: **CLI flag → `STOCKFISH_PATH` env var → `stockfish` on
PATH**. Pick one:

```bash
# (a) per-invocation flag
moveexp --engine-path ~/tools/stockfish analyze-move --fen "..." --move e2e4

# (b) env var (persistent; put in ~/.bashrc or ~/.config/environment.d)
export STOCKFISH_PATH="$HOME/tools/stockfish"

# (c) on PATH
ln -s ~/tools/stockfish ~/.local/bin/stockfish    # ensure ~/.local/bin is on PATH
```

If none resolves, the tool fails with: *"could not start UCI engine … Install Stockfish 16+
or pass --engine-path / STOCKFISH_PATH."*

---

## 3. Data directory

All downloads, the engine cache, and generated datasets live under `data/` by default
(`<repo>/data`). Override it with either the env var or the CLI flag:

```bash
export MOVEXP_DATA_DIR="$HOME/chess-ai-data"      # env var (persistent)

moveexp --data-dir "$HOME/chess-ai-data" analyze-move --fen "..." --move e2e4
```

The per-command `--cache-db` and `--out` flags still take precedence over `--data-dir`.

---

## 4. NixOS: making numpy / pandas / pyarrow import

Binary wheels for `numpy`, `pandas`, `pyarrow` are linked against the system GCC's C++
runtime (`libstdc++.so.6`), which NixOS does not put on the default loader path. Two options:

### Option A — the `shell.nix` dev shell (recommended)

```bash
nix-shell            # drops you in a shell with libstdc++ on LD_LIBRARY_PATH
python -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]'
python scripts/check_env.py
```

### Option B — nix-ld (no dev shell)

If you use a plain venv rather than `nix-shell`, enable `nix-ld` in your NixOS config:

```nix
{ config, pkgs, ... }: {
  programs.nix-ld = {
    enable = true;
    libraries = with pkgs; [ stdenv.cc.cc.lib zlib ];
  };
}
```

Then `sudo nixos-rebuild switch` and create the venv as in §1; no `LD_LIBRARY_PATH` export is
needed because nix-ld injects the libraries globally.

---

## 5. Verify the environment

```bash
. .venv/bin/activate
python scripts/check_env.py --engine ~/tools/stockfish
```

Expected: a `PASS` line for each import and for the Stockfish `uci` handshake (with the
engine's name, e.g. `Stockfish 19`), ending in `ALL CHECKS PASSED`.

---

## 6. Run the tests

```bash
. .venv/bin/activate
export STOCKFISH_PATH="$HOME/tools/stockfish"

pytest                              # full suite; engine tests use $STOCKFISH_PATH
pytest -m engine                    # only the tests that really start Stockfish
ruff check src tests eval scripts   # lint
ruff format --check src tests eval scripts
```
