# -*- coding: utf-8 -*-
"""自动查找 ArcGIS Pro 自带 python.exe（仅标准库，任意 Python 均可运行本脚本）"""
import os
import string
import sys
import winreg

PRO_PY_SUFFIX = os.path.join(
    "bin", "Python", "envs", "arcgispro-py3", "python.exe"
)


def _norm(path):
    return os.path.normpath(path) if path else ""


def _is_pro_python(path):
    if not path:
        return False
    low = path.replace("/", "\\").lower()
    return "arcgispro-py3" in low and low.endswith("\\python.exe")


def _candidate_from_root(root):
    if not root:
        return ""
    root = _norm(root.rstrip("\\/"))
    if root.lower().endswith("\\bin"):
        root = os.path.dirname(root)
    cand = _norm(os.path.join(root, PRO_PY_SUFFIX))
    return cand if os.path.isfile(cand) else ""


def _registry_install_dirs():
    dirs = []
    seen = set()

    def add(path):
        path = _norm(path or "")
        if path and path not in seen:
            seen.add(path)
            dirs.append(path)

    key_paths = (
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\ESRI\ArcGISPro"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\ESRI\ArcGISPro"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\ESRI\ArcGISPro"),
    )
    value_names = ("InstallDir", "InstallPath", "InstallFolder", "InstallLocation")

    for hive, sub in key_paths:
        try:
            with winreg.OpenKey(hive, sub) as key:
                for name in value_names:
                    try:
                        add(winreg.QueryValueEx(key, name)[0])
                    except OSError:
                        pass
        except OSError:
            continue

    uninstall_roots = (
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    )
    for hive, sub in uninstall_roots:
        try:
            with winreg.OpenKey(hive, sub) as root:
                for i in range(winreg.QueryInfoKey(root)[0]):
                    try:
                        name = winreg.EnumKey(root, i)
                        with winreg.OpenKey(root, name) as item:
                            try:
                                display, _ = winreg.QueryValueEx(item, "DisplayName")
                            except OSError:
                                continue
                            if not display or "ArcGIS Pro" not in display:
                                continue
                            for val in ("InstallLocation", "InstallSource", "DisplayIcon"):
                                try:
                                    add(winreg.QueryValueEx(item, val)[0])
                                except OSError:
                                    pass
                    except OSError:
                        continue
        except OSError:
            continue

    return dirs


def _fixed_candidates():
    roots = []
    for env_name in ("ProgramFiles", "ProgramFiles(x86)", "LocalAppData"):
        base = os.environ.get(env_name, "")
        if base:
            roots.append(os.path.join(base, "ArcGIS", "Pro"))
    roots.extend(
        [
            r"C:\ArcGIS\Pro",
            r"D:\ArcGIS\Pro",
            r"E:\ArcGIS\Pro",
            r"F:\ArcGIS\Pro",
            r"D:\Program Files\ArcGIS\Pro",
            r"E:\Program Files\ArcGIS\Pro",
        ]
    )
    for letter in string.ascii_uppercase:
        roots.append(f"{letter}:\\ArcGIS\\Pro")
        roots.append(f"{letter}:\\Program Files\\ArcGIS\\Pro")
    return roots


def iter_pro_python_paths():
    ordered = []
    seen = set()

    def push(path):
        path = _norm(path)
        if not path or path in seen or not os.path.isfile(path):
            return
        if not _is_pro_python(path):
            return
        seen.add(path)
        ordered.append(path)

    tool_dir = os.path.dirname(os.path.abspath(__file__))
    cfg = os.path.join(tool_dir, "python_path.txt")
    if os.path.isfile(cfg):
        with open(cfg, "r", encoding="utf-8-sig") as f:
            push(f.readline().strip().strip('"'))

    for root in _registry_install_dirs():
        push(_candidate_from_root(root))

    for root in _fixed_candidates():
        push(_candidate_from_root(root))

    return ordered


def find_pro_python():
    paths = iter_pro_python_paths()
    return paths[0] if paths else ""


def main():
    path = find_pro_python()
    if not path:
        sys.exit(1)
    print(path, end="")


if __name__ == "__main__":
    main()
