# -*- coding: utf-8 -*-
"""手动指定 ArcGIS Pro 的 python.exe（及可选 ArcGISPro.exe）"""
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox


def _tool_dir():
    return os.path.dirname(os.path.abspath(__file__))


def _save_python(path):
    path = os.path.normpath(path)
    low = path.replace("/", "\\").lower()
    if "arcgispro-py3" not in low:
        messagebox.showerror(
            "路径不对",
            "请选择 ArcGIS Pro 自带的 python.exe：\n\n"
            "…\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe",
        )
        return None
    ok, msg = _verify_arcpy(path)
    if not ok:
        if not messagebox.askyesno(
            "arcpy 预检未通过",
            "未能在此路径立即 import arcpy（Pro 已安装时也可能出现）：\n\n"
            f"{msg}\n\n"
            "若你确认选的是 arcgispro-py3\\python.exe，仍要保存吗？",
        ):
            return None
    cfg = os.path.join(_tool_dir(), "python_path.txt")
    with open(cfg, "w", encoding="utf-8") as f:
        f.write(path)
    return cfg


def _verify_arcpy(python_exe):
    import subprocess

    tool = os.path.join(_tool_dir(), "verify_pro_python.py")
    if os.path.isfile(tool):
        try:
            r = subprocess.run(
                [sys.executable, tool, python_exe],
                capture_output=True,
                text=True,
                timeout=200,
            )
            if r.returncode == 0:
                return True, ""
            return False, (r.stderr or r.stdout or "verify failed").strip()[:300]
        except OSError as e:
            return False, str(e)
    try:
        r = subprocess.run(
            [python_exe, "-c", "import arcpy"],
            capture_output=True,
            text=True,
            timeout=180,
        )
    except OSError as e:
        return False, str(e)
    if r.returncode == 0:
        return True, ""
    return False, (r.stderr or r.stdout or "import arcpy failed").strip()[:300]


def _save_pro_exe(path):
    cfg = os.path.join(_tool_dir(), "arcgispro_path.txt")
    with open(cfg, "w", encoding="utf-8") as f:
        f.write(os.path.normpath(path))


def main():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(
        "配置路径",
        "请选择 ArcGIS Pro 自带的 python.exe\n\n"
        "通常在：\n"
        "…\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe",
    )
    py = filedialog.askopenfilename(
        title="选择 python.exe",
        filetypes=[("python.exe", "python.exe"), ("可执行文件", "*.exe")],
    )
    if not py:
        messagebox.showwarning("已取消", "未保存任何路径。")
        return 1
    if os.path.basename(py).lower() != "python.exe":
        if not messagebox.askyesno("确认", f"所选文件不是 python.exe：\n{py}\n\n仍要保存吗？"):
            return 1
    cfg = _save_python(py)
    if not cfg:
        return 1
    messagebox.showinfo("已保存", f"Python 路径已写入：\n{cfg}\n\n{py}")

    if messagebox.askyesno("可选", "是否同时记录 ArcGISPro.exe 位置？（仅备忘，非必须）"):
        pro = filedialog.askopenfilename(
            title="选择 ArcGISPro.exe",
            filetypes=[("ArcGISPro.exe", "ArcGISPro.exe"), ("可执行文件", "*.exe")],
        )
        if pro:
            _save_pro_exe(pro)
            messagebox.showinfo("已保存", pro)
    return 0


if __name__ == "__main__":
    sys.exit(main())
