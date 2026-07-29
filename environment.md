# 项目运行环境

## 目标环境

| 工具 | 目标 |
| --- | --- |
| Python | 3.14，项目虚拟环境 |
| MiKTeX | 26.1 |
| LaTeX | XeLaTeX + latexmk |
| R | 待统一并验证 VS Code 集成 |

## 2026-07-29 本机审计

- `python` 当前默认指向 Python 3.11.9。
- Python 3.14.0 位于 `C:/Users/stemh/AppData/Local/Programs/Python/Python314/python.exe`。
- 已用 Python 3.14.0 建立项目虚拟环境 `.venv/`，并成功安装
  `requirements-dev.txt` 中的全部建模库和测试库。
- MiKTeX 26.1、XeLaTeX 和 latexmk 4.87 可找到。
- 当前发现 R 4.5.2 位于 `D:/R-4.5.2`，未加入 PATH；未确认 R 4.6。

## CMD 使用方式

```bat
cd /d C:\Users\stemh\Desktop\国赛_作业
.venv\Scripts\activate
python --version
python -m pip install -r requirements-dev.txt
```

正式复现使用 `.venv\Scripts\python.exe`，不能仅运行指向 Python 3.11 的全局
`python`。`.venv/` 是本机环境且已被 Git 忽略；依赖声明以
`requirements.txt` 和 `requirements-dev.txt` 为准。
