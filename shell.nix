# Dev shell for the moveexp project on NixOS.
#
# Provides Python and puts the shared libraries that pip-installed manylinux wheels link
# against onto LD_LIBRARY_PATH. NixOS keeps these off the default loader path, so without
# this `import numpy` fails with errors such as:
#
#   ImportError: libstdc++.so.6: cannot open shared object file   (numpy, pandas, pyarrow)
#   ImportError: libz.so.1: cannot open shared object file       (numpy)
#   ImportError: libzstd.so.1: cannot open shared object file    (pyarrow, zstandard)
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

  #: Libraries the binary wheels are dynamically linked against. Listed once and reused for
  #: both the shell's `packages` (so they are in the closure) and LD_LIBRARY_PATH.
  runtimeLibs = [
    pkgs.stdenv.cc.cc.lib # libstdc++.so.6, libgcc_s.so.1
    pkgs.zlib # libz.so.1
    pkgs.zstd # libzstd.so.1
  ];
in
pkgs.mkShell {
  packages = [ python ] ++ runtimeLibs;

  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath runtimeLibs}''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    echo "moveexp dev shell: $(python --version)"
    echo "Next: python -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]'"
  '';
}
