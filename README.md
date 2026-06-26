# Simple GIS Assistant App (Homework)

简易 GIS 辅助应用（作业）— ArcGIS Pro 交付版。

## 环境要求

- 已安装 **ArcGIS Pro**（含 arcpy）
- Windows 10/11

## 首次使用

1. 运行 `configure_path.bat`（或 `配置路径.bat`），选择本机 Pro 的 `python.exe`
2. 运行 `install_deps.bat`（或 `安装依赖.bat`），看到 **VERIFY OK** 即成功
3. 双击 **`launcher.exe`** 启动（请勿直接运行 `app/` 内脚本）

## 数据格式

- **ArcGIS Pro**：`.gdb` 文件夹
- **ArcMap 10.x**：`.mdb` 个人地理数据库（选择后会自动导入到 `尝试/_mdb_cache/*.gdb`）

## 说明

- 本仓库为**加密交付版**，核心逻辑位于 `app/py39` 与 `app/py311`
- 打包时请保留 `app/**/pyarmor_runtime.pyd` 与 `launcher.exe`
- 成果默认输出到 `尝试/` 目录（运行时自动创建）

详细说明见 [使用说明.txt](使用说明.txt)。
