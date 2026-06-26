# -*- coding: utf-8 -*-
"""Check pydeps imports and PyQt5 GUI runtime (used by install_deps.bat)."""
import os
import sys

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOL_DIR not in sys.path:
    sys.path.insert(0, TOOL_DIR)

from pydeps_runtime import check_gui, configure  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print("usage: verify_deps.py <pydeps_dir>", file=sys.stderr)
        sys.exit(2)

    deps = sys.argv[1]
    ok, msg = configure(deps)
    if not ok:
        print(msg, file=sys.stderr)
        sys.exit(1)

    import numpy as np

    print(f"Pro numpy {np.__version__}", flush=True)
    import matplotlib  # noqa: F401
    import openpyxl  # noqa: F401
    import PyQt5  # noqa: F401

    try:
        check_gui()
    except Exception as e:
        print(f"PyQt5 GUI check failed: {e}", file=sys.stderr)
        sys.exit(1)

    print("VERIFY OK")


if __name__ == "__main__":
    main()
