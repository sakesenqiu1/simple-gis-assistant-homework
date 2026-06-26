# -*- coding: utf-8 -*-
"""启动入口（发布版用；开发版请直接运行 main_gui.py）"""
import os
import sys


def _root_dir():
    return os.path.dirname(os.path.abspath(__file__))


def _pyarmor_tag():
    major, minor = sys.version_info[:2]
    if (major, minor) == (3, 9):
        return "py39"
    if (major, minor) >= (3, 11):
        return "py311"
    return ""


def _resolve_app_dir(root):
    """返回 (app_dir, mode)；mode 为 py39/py311/legacy/dev。"""
    tag = _pyarmor_tag()
    candidates = []
    if tag:
        candidates.append(tag)
    for t in ("py311", "py39"):
        if t not in candidates:
            candidates.append(t)
    candidates.append("")

    for item in candidates:
        if item:
            app = os.path.join(root, "app", item)
            mode = item
        else:
            app = os.path.join(root, "app")
            mode = "legacy"
        pyd = os.path.join(app, "pyarmor_runtime_000000", "pyarmor_runtime.pyd")
        if os.path.isfile(pyd):
            return app, mode

    if os.path.isfile(os.path.join(root, "main_gui.py")):
        return root, "dev"

    if tag:
        return os.path.join(root, "app", tag), tag
    return os.path.join(root, "app"), "legacy"


def _app_dir(root):
    app, _mode = _resolve_app_dir(root)
    return app


def _setup_paths(root):
    os.environ["GIS_TOOL_ROOT"] = root
    os.chdir(root)
    deps = os.path.join(root, "pydeps")
    if os.path.isdir(deps):
        os.environ["GIS_PYDEPS"] = deps
    tool_dir = os.path.dirname(os.path.abspath(__file__))
    if tool_dir not in sys.path:
        sys.path.insert(0, tool_dir)
    app, mode = _resolve_app_dir(root)
    if mode == "dev":
        for p in (tool_dir, root):
            if p not in sys.path:
                sys.path.insert(0, p)
    elif os.path.isdir(app) and app not in sys.path:
        sys.path.insert(0, app)


def _configure_pydeps(root):
    deps = os.environ.get("GIS_PYDEPS") or os.path.join(root, "pydeps")
    if not os.path.isdir(deps):
        return True
    from pydeps_runtime import configure

    ok, msg = configure(deps)
    if not ok:
        _show_error(
            "依赖不完整",
            f"{msg}\n\n请重新运行 install_deps.bat（需联网）。",
        )
        return False
    return True


def _missing_packages():
    missing = []
    for pkg in ("PyQt5", "matplotlib", "openpyxl"):
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    return missing


def _show_error(title, message):
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)
    except Exception:
        print(title, message, file=sys.stderr)


def check_environment():
    missing = _missing_packages()
    if not missing:
        return True
    _show_error(
        "缺少依赖库",
        "当前 ArcGIS Pro Python 中未安装：\n"
        + "、".join(missing)
        + "\n\n请双击「安装依赖.bat」（需联网一次）。",
    )
    return False


def _check_pyarmor_runtime(root):
    app, mode = _resolve_app_dir(root)
    if mode == "dev":
        return True

    pyd = os.path.join(app, "pyarmor_runtime_000000", "pyarmor_runtime.pyd")
    ver = ".".join(map(str, sys.version_info[:2]))
    tag = _pyarmor_tag()
    if not tag:
        _show_error(
            "Python 版本不支持",
            f"本机 ArcGIS Pro Python：{ver}\n\n"
            "本工具支持 Python 3.9（Pro 3.0–3.2）"
            "与 Python 3.11（Pro 3.3+）。",
        )
        return False
    if os.path.isfile(pyd):
        return True

    missing = []
    for t in ("py39", "py311"):
        p = os.path.join(root, "app", t, "pyarmor_runtime_000000", "pyarmor_runtime.pyd")
        missing.append(f"  app\\{t}\\…\\pyarmor_runtime.pyd  {'存在' if os.path.isfile(p) else '缺失'}")

    _show_error(
        "文件不完整",
        f"缺少加密运行时（当前需要 app\\{tag}\\…\\pyarmor_runtime.pyd）。\n\n"
        + "\n".join(missing)
        + "\n\n请重新解压完整 zip，勿只复制部分文件。\n"
        "（微信/QQ 可能拦截 .pyd，请换网盘）",
    )
    return False


def _check_arcpy():
    try:
        import arcpy  # noqa: F401
        return True
    except ImportError:
        _show_error(
            "未找到 arcpy",
            "当前 Python 不是 ArcGIS Pro 自带环境。\n\n"
            "请重新运行 configure_path.bat，手动选择：\n"
            "…\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe\n\n"
            "不要选 C:\\Python、Anaconda 或其它 python.exe。",
        )
        return False


def run_app():
    root = _root_dir()
    _setup_paths(root)
    if not _check_pyarmor_runtime(root):
        sys.exit(1)
    if not _check_arcpy():
        sys.exit(1)
    if not _configure_pydeps(root):
        sys.exit(1)
    if not check_environment():
        sys.exit(1)
    try:
        from main_gui import main
    except ImportError as e:
        msg = str(e)
        ver = ".".join(map(str, sys.version_info[:2]))
        if "DLL load failed" in msg or "pyarmor_runtime" in msg:
            _show_error(
                "加密运行时加载失败",
                f"本机 ArcGIS Pro Python：{ver}\n\n"
                "请确认已解压 app\\py39 与 app\\py311 两个文件夹，"
                "且其中的 .pyd 未被杀毒软件删除。\n\n"
                "仍失败请重新下载完整 zip。",
            )
        else:
            _show_error("启动失败", msg)
        sys.exit(1)
    main()


if __name__ == "__main__":
    run_app()
