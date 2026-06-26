# -*- coding: utf-8 -*-
"""校验 python.exe 是否为 ArcGIS Pro 环境（能 import arcpy）"""
import os
import subprocess
import sys


def _pro_root_from_python(python_exe):
    low = python_exe.replace("/", "\\").lower()
    marker = "\\envs\\arcgispro-py3\\"
    idx = low.find(marker)
    if idx < 0:
        return ""
    # ...\Pro\bin\Python\envs\arcgispro-py3\python.exe
    python_dir = python_exe[: idx + len(marker) - 1]
    bin_dir = os.path.dirname(os.path.dirname(python_dir))  # ...\Pro\bin
    return os.path.dirname(bin_dir)  # ...\Pro


def _runtime_env(python_exe):
    env = os.environ.copy()
    python_exe = os.path.normpath(python_exe)
    py_home = os.path.dirname(python_exe)
    py_scripts = os.path.join(py_home, "Scripts")
    pro_root = _pro_root_from_python(python_exe)
    bin_dir = os.path.join(pro_root, "bin") if pro_root else ""
    path_parts = [p for p in (bin_dir, py_home, py_scripts) if p and os.path.isdir(p)]
    if path_parts:
        env["PATH"] = os.pathsep.join(path_parts + [env.get("PATH", "")])
    if pro_root:
        env.setdefault("ARCGISPROAPP", os.path.join(pro_root, "bin"))
    return env, bin_dir or py_home


def verify_python(path):
    path = path.strip().strip('"')
    if not path:
        return False, "路径为空"
    if "arcgispro-py3" not in path.replace("/", "\\").lower():
        return (
            False,
            "这不是 ArcGIS Pro 的 arcgispro-py3 环境。\n"
            "请选择 …\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe",
        )
    if not os.path.isfile(path):
        return False, f"文件不存在：{path}"
    env, cwd = _runtime_env(path)
    try:
        r = subprocess.run(
            [path, "-c", "import arcpy; print('OK')"],
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
            cwd=cwd if os.path.isdir(cwd) else None,
        )
    except subprocess.TimeoutExpired:
        return False, "import arcpy 超时（首次可能较慢，请重试或先打开一次 ArcGIS Pro）"
    except OSError as e:
        return False, str(e)
    if r.returncode == 0:
        return True, ""
    err = (r.stderr or r.stdout or "import arcpy failed").strip()
    if len(err) > 300:
        err = err[:300] + "..."
    if "License" in err or "license" in err:
        err += "\n\n提示：Pro 界面能打开不代表命令行已授权，请先登录 Pro 后再试。"
    return False, err


def main():
    if len(sys.argv) < 2:
        print("usage: verify_pro_python.py <python.exe>", file=sys.stderr)
        sys.exit(2)
    ok, msg = verify_python(sys.argv[1])
    if ok:
        print("OK")
        sys.exit(0)
    print(msg, file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
