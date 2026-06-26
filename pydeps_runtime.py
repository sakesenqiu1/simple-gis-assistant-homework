# -*- coding: utf-8 -*-
"""Configure pydeps without breaking ArcGIS Pro numpy/arcpy."""
import glob
import os
import shutil
import sys

# pip --target 可能带入与 Pro 冲突的包，必须删掉，改用 Pro 自带版本
_CONFLICT_NAMES = (
    "numpy",
    "numpy.libs",
    "pyarrow",
    "pandas",
    "scipy",
    "scipy.libs",
)


def strip_pro_conflicts(deps_root):
    deps_root = os.path.abspath(deps_root)
    if not os.path.isdir(deps_root):
        return
    for name in _CONFLICT_NAMES:
        path = os.path.join(deps_root, name)
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
    for pattern in (
        "numpy-*.dist-info",
        "pyarrow-*.dist-info",
        "pandas-*.dist-info",
        "scipy-*.dist-info",
    ):
        for path in glob.glob(os.path.join(deps_root, pattern)):
            shutil.rmtree(path, ignore_errors=True)


def configure(deps_root):
    deps_root = os.path.abspath(os.path.normpath(deps_root))
    if not os.path.isdir(deps_root):
        return False, "pydeps folder missing"

    strip_pro_conflicts(deps_root)

    if deps_root not in sys.path:
        sys.path.insert(0, deps_root)

    qwindows = os.path.join(
        deps_root, "PyQt5", "Qt5", "plugins", "platforms", "qwindows.dll"
    )
    if not os.path.isfile(qwindows):
        return False, f"missing Qt plugin: {qwindows}"

    qt_bin = os.path.join(deps_root, "PyQt5", "Qt5", "bin")
    qt_plugins = os.path.join(deps_root, "PyQt5", "Qt5", "plugins")
    platforms = os.path.join(qt_plugins, "platforms")

    if os.path.isdir(qt_bin):
        os.environ["PATH"] = qt_bin + os.pathsep + os.environ.get("PATH", "")
        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(qt_bin)

    os.environ["QT_PLUGIN_PATH"] = qt_plugins
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = platforms
    return True, ""


def check_gui():
    from PyQt5.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    return app is not None
