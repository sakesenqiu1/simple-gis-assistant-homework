# -*- coding: utf-8 -*-
"""Install pydeps compatible with ArcGIS Pro numpy (no numpy in pydeps)."""
import os
import subprocess
import sys

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOL_DIR not in sys.path:
    sys.path.insert(0, TOOL_DIR)

from pydeps_runtime import strip_pro_conflicts  # noqa: E402


def _mpl_version():
    import numpy as np

    parts = [int(x) for x in np.__version__.split(".")[:2]]
    major, minor = parts[0], parts[1]
    if (major, minor) < (1, 23):
        return "3.5.3"
    if (major, minor) < (1, 26):
        return "3.7.5"
    return "3.8.4"


def _pip(deps, index, *packages):
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--proxy=",
        "--trusted-host",
        "pypi.org",
        "--trusted-host",
        "files.pythonhosted.org",
        "--trusted-host",
        "pypi.tuna.tsinghua.edu.cn",
        f"--target={deps}",
        "--no-deps",
        "-i",
        index,
        *packages,
    ]
    subprocess.run(cmd, check=True)


def _install_once(deps, index):
    mpl = _mpl_version()
    print(f"Pro numpy OK, install matplotlib=={mpl} into pydeps ...", flush=True)

    _pip(deps, index, "PyQt5", "PyQt5-Qt5", "PyQt5-sip", f"matplotlib=={mpl}", "openpyxl")

    extras = [
        "pillow",
        "cycler",
        "kiwisolver",
        "fonttools",
        "packaging",
        "pyparsing",
        "python-dateutil",
        "et-xmlfile",
        "importlib-resources",
    ]
    if mpl >= "3.7":
        extras.append("contourpy")
    _pip(deps, index, *extras)

    strip_pro_conflicts(deps)
    print("Removed numpy/pyarrow/scipy from pydeps (use Pro built-in).", flush=True)


def main():
    if len(sys.argv) < 2:
        print("usage: install_pydeps.py <pydeps_dir>", file=sys.stderr)
        sys.exit(2)

    deps = os.path.abspath(sys.argv[1])
    os.makedirs(deps, exist_ok=True)

    mirrors = (
        "https://pypi.org/simple",
        "https://pypi.tuna.tsinghua.edu.cn/simple",
    )
    last_err = None
    for url in mirrors:
        try:
            print(f"Try mirror: {url}", flush=True)
            _install_once(deps, url)
            break
        except subprocess.CalledProcessError as e:
            last_err = e
    else:
        print(f"pip install failed: {last_err}", file=sys.stderr)
        sys.exit(1)

    from verify_deps import main as verify_main

    sys.argv = [sys.argv[0], deps]
    verify_main()


if __name__ == "__main__":
    main()
