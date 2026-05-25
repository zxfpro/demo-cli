# demo-cli

一个极简 Python CLI 开发框架（`pyproject.toml + Typer`）。

## 1) 本地开发（极简）

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

运行：

```bash
demo --help
demo hello
demo hello Alice
demo version
```

## 2) GitHub Public 分发 + pip 安装

把仓库公开后，用户可直接安装：

```bash
pip install "git+https://github.com/yourname/demo-cli.git"
```

如果使用 tag（推荐）：

```bash
pip install "git+https://github.com/yourname/demo-cli.git@v0.1.0"
```

## 3) 极简开发方式

- 所有命令都放在 `src/demo_cli/cli.py`
- 每个命令就是一个 `@app.command()` 函数
- 发布时只改：
  - `pyproject.toml` 的 `version`
  - `src/demo_cli/__init__.py` 的 `__version__`

## 4) 新增命令示例

```python
@app.command()
def add(x: int, y: int) -> None:
    typer.echo(x + y)
```

## 5) 可选：发布到 PyPI

```bash
pip install build twine
python -m build
python -m twine upload dist/*
```

发布后用户可直接：

```bash
pip install demo-cli
```
