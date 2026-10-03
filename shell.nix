# Dev shell for the moveexp project on NixOS.
#
# Provides Python and puts the C++ standard library (libstdc++.so.6) on LD_LIBRARY_PATH so
# that pip-installed binary wheels (numpy, pandas, pyarrow) load without a manual export.
#
# Usage:
#   nix-shell                       # enter the shell
#   python -m venv .venv
#   . .venv/bin/activate
#   pip install -e '.[dev]'
#   python scripts/check_env.py
#
# If you cannot use nix-shell (e.g. non-NixOS with Nix, or a locked-down channel), enable
# nix-ld instead — see docs/SETUP.md.
{ pkgs ? import <nixpkgs> { } }:

let
  python = pkgs.python313;
in
pkgs.mkShell {
  packages = [
    python
    # Provides libstdc++.so.6, which binary wheels linked against the system GCC need.
    pkgs.stdenv.cc.cc.lib
  ];

  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    echo "moveexp dev shell: $(python --version)"
    echo "Next: python -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]'"
  '';
}
